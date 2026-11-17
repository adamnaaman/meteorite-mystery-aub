"""The Map That Misleads: a reproducible meteorite recovery data story."""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="The Map That Misleads | Meteorite Mystery", page_icon="☄️", layout="wide", initial_sidebar_state="collapsed")
ROOT = Path(__file__).parent
NAVY = "#10263A"
BLUE = "#38799F"
TEAL = "#0B8279"
CORAL = "#E9954C"
CREAM = "#F7F8F6"
GRAY = "#66798B"

st.markdown("""<style>
:root{color-scheme:light;} .stApp{background:#f8fafb;color:#10263a}
.block-container{padding-top:1.15rem;padding-bottom:3rem;max-width:1150px}
h1,h2,h3{letter-spacing:-.025em;color:#10263a}
h1{font-size:clamp(2.1rem,5vw,3.8rem)!important;line-height:1.12!important}
h2{margin-top:1.9rem!important}
p{line-height:1.65}
.story-kicker{font-size:.75rem;letter-spacing:.18em;font-weight:750;color:#267a87;text-transform:uppercase}
.story-sub{font-size:1.19rem;color:#465e73;margin-bottom:1rem}
.story-note{font-size:.9rem;color:#516679;border-left:3px solid #d6a05e;padding:.45rem .9rem;background:#f3f5f4;border-radius:0 8px 8px 0}
.stat-card{background:white;border:1px solid #dee6e9;border-radius:14px;padding:1.05rem 1.1rem;height:100%}
.stat-number{font-size:clamp(1.6rem,3vw,2.4rem);font-weight:750;color:#10263a}
.stat-label{font-size:.89rem;color:#617587}
div[data-testid="stPlotlyChart"]{background:#fff;border:1px solid #e1e8ea;border-radius:14px;padding:.3rem}
[data-testid="stSidebar"]{background:#fff}
@media (max-width: 680px){.block-container{padding:1rem .85rem 2rem} h1{font-size:2rem!important}.story-sub{font-size:1.05rem}}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    d = pd.read_csv(ROOT / "meteorites_cleaned.csv", low_memory=False)
    d["recovery_year"] = pd.to_numeric(d["recovery_year"], errors="coerce")
    d["latitude"] = pd.to_numeric(d["latitude"], errors="coerce")
    d["longitude"] = pd.to_numeric(d["longitude"], errors="coerce")
    d["mass_g"] = pd.to_numeric(d["mass_g"], errors="coerce")
    return d

df = load_data()
N = len(df)
M = df[df["location_usable"] == 1].copy()
ANT = M[M["antarctic_latitude"] == 1]
FELL = int((df["fall_status"] == "Fell").sum())
FOUND = int((df["fall_status"] == "Found").sum())
INVALID = N-len(M)
assert (N,len(M),len(ANT),FOUND,FELL,INVALID) == (45716,32186,22099,44609,1107,13530), "Unexpected dataset counts; review the cleaning pipeline"


def fig_style(fig, height=380, margin=None):
    fig.update_layout(template="plotly_white", height=height, margin=margin or dict(l=12,r=12,t=26,b=25),
      font=dict(family="Arial, sans-serif",color=NAVY), paper_bgcolor="white", plot_bgcolor="white", showlegend=False)
    return fig

st.markdown('<div class="story-kicker">A DATA STORY · NASA METEORITE LANDINGS</div>',unsafe_allow_html=True)
st.title("The Map That Misleads")
st.markdown('<div class="story-sub">Why does Antarctica dominate the world’s meteorite discovery records?</div>',unsafe_allow_html=True)
st.markdown("**Imagine plotting every meteorite in a historical scientific catalog.** You might expect a reasonably scattered world map. Instead, an astonishing number of mapped records cluster close to the South Pole. Does Antarctica attract space rocks—or does our view of the evidence have a blind spot?")

c1,c2,c3=st.columns(3)
for c,num,desc in [(c1,f"{N:,}","Cataloged meteorite records"),(c2,f"{len(M):,}","Records with usable coordinates"),(c3,f"{len(ANT)/len(M):.1%}","Mapped records at ≥60° south")]:
    with c: st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{desc}</div></div>',unsafe_allow_html=True)

st.header("01 · The geographic mystery")
st.write("Of the **32,186 mapped records**, **22,099** lie at Antarctic latitudes (60°S or farther south). That's **68.7%** of records we can map—not 68.7% of all meteorites that have ever fallen.")

groups = pd.DataFrame({"Location":["Antarctic latitudes", "Other mapped latitudes", "Unknown / invalid location"],"Records":[len(ANT),len(M)-len(ANT),INVALID]})
fig=px.bar(groups,x="Records",y="Location",orientation="h",color="Location", color_discrete_map={"Antarctic latitudes":TEAL,"Other mapped latitudes":BLUE,"Unknown / invalid location":"#A7B5C1"},text="Records")
fig.update_traces(texttemplate="%{text:,}",textposition="outside",cliponaxis=False)
fig.update_yaxes(categoryorder="array",categoryarray=list(reversed(groups.Location)),title=None)
fig.update_xaxes(title="Number of records",gridcolor="#edf1f4",range=[0,26000]);fig_style(fig,330)
st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
st.markdown('<div class="story-note"><b>Why keep the unknown category?</b> 13,530 records cannot be reliably located on a map. Dropping them invisibly would make the geographic story look more complete than it is.</div>',unsafe_allow_html=True)

st.header("02 · The difference between falling and being found")
st.write("The dataset separates **‘Fell’**—a fall that was observed—from **‘Found’**—a meteorite recovered sometime after it landed. It is not a measure of how often meteorites actually fall in each place.")
f1,f2=st.columns([1.2,1])
with f1:
    f=go.Figure(go.Bar(x=["Found later","Observed falling"],y=[FOUND,FELL],marker_color=[TEAL,CORAL],text=[f"{FOUND:,}",f"{FELL:,}"],textposition="outside"))
    f.update_yaxes(title="Catalog records",gridcolor="#edf1f4",range=[0,50000]); fig_style(f,355)
    st.plotly_chart(f,width="stretch",config={"displayModeBar":False})
with f2:
    st.metric("Cataloged as ‘Found’",f"{FOUND/N:.1%}")
    st.metric("Cataloged as ‘Fell’",f"{FELL/N:.1%}")
    st.markdown("**All 22,099 Antarctic-latitude records in this mapped subset are labeled ‘Found’.** This pattern is consistent with recovery practices, not evidence of an unusual meteorite-fall rate.")

st.header("03 · Explore the recovery map")
st.write("Explore where usable locations are recorded. The symbols represent **cataloged meteorite records**; larger symbols reflect multiple records in a geographic grid cell. This avoids plotting tens of thousands of unreadable overlapping markers.")

ctl1,ctl2 = st.columns([1,1])
with ctl1:
    region=st.selectbox("Geographic focus", ["World","Antarctica (southern hemisphere)","Outside Antarctic latitudes"])
with ctl2:
    status=st.selectbox("Observed fall or later find",["All records","Found","Fell"])

filtered=M
if region=="Antarctica (southern hemisphere)":filtered=filtered[filtered.antarctic_latitude==1]
elif region=="Outside Antarctic latitudes":filtered=filtered[filtered.antarctic_latitude==0]
if status!="All records":filtered=filtered[filtered.fall_status==status]

# Bin globally in 2° squares (separate Antarctic detail uses 1° cells).
step=1 if region=="Antarctica (southern hemisphere)" else 2
mapped=filtered.assign(lat_bin=(np.floor(filtered.latitude/step)*step +step/2),lon_bin=(np.floor(filtered.longitude/step)*step+step/2))
bins=mapped.groupby(["lat_bin","lon_bin"],as_index=False).agg(records=("meteorite_id","size"),example=("name","first"))
if bins.empty:
    st.info("No records match these settings.")
else:
    max_count=int(bins.records.max())
    sizes=(5+19*(np.sqrt(bins.records)/np.sqrt(max_count))).clip(5,25)
    geo=go.Figure()
    geo.add_trace(go.Scattergeo(lon=bins.lon_bin,lat=bins.lat_bin,mode="markers",
      marker=dict(size=sizes,color=np.log1p(bins.records),colorscale=[[0,"#65a5bc"],[.4,"#167a89"],[1,"#e49c4b"]],opacity=.82,line=dict(width=.4,color="#fff"),showscale=True,colorbar=dict(title="log(1+n)",len=.58,thickness=10)),
      text=[f"{n:,} recorded meteorite(s) in grid cell" for n in bins.records],hovertemplate="%{text}<extra></extra>"))
    geo.update_geos(projection_type="orthographic" if region=="Antarctica (southern hemisphere)" else "natural earth", projection_rotation=dict(lon=0,lat=-90) if region=="Antarctica (southern hemisphere)" else dict(lon=0,lat=0),showcoastlines=True,coastlinecolor="#82949d",showland=True,landcolor="#e7ebeb",showocean=True,oceancolor="#e7f1f4",showlakes=False,showframe=False,bgcolor="white")
    fig_style(geo,490,dict(l=0,r=0,t=5,b=0))
    st.plotly_chart(geo,width="stretch",config={"displayModeBar":True,"scrollZoom":False})
    st.caption(f"{len(filtered):,} source records represented by {len(bins):,} spatial grid cells. Binning is for display only; summary statistics use original individual records.")

with st.expander("Explore individual meteorites"):
    options = st.multiselect("Filter classification", sorted(df.classification.dropna().unique()),default=[],max_selections=10)
    subset=filtered if not options else filtered[filtered.classification.isin(options)]
    st.dataframe(subset[["name","classification","fall_status","recovery_year","mass_g","latitude","longitude"]].head(500),hide_index=True,width="stretch")
    st.caption("Preview limited to 500 rows. Download the full cleaned dataset for unrestricted analysis.")

st.header("04 · What the map really tells us")
st.markdown("The concentration is not a cosmic preference for Antarctica. Antarctica's blue-ice areas, cold dry conditions, and scientific search programs make many meteorites easier to **preserve, expose, and recover**. By contrast, meteorites in vegetation, cities, or oceans may go unnoticed. The map is therefore partly a map of **human discovery opportunity**.")
st.markdown("**The lesson for analytics:** a dataset can be accurate about what was *recorded* yet misleading about what actually *happened*. Before using a striking map to infer a natural process, ask how observations entered the database.")
st.info("**Main takeaway:** A map of discoveries is not necessarily a map of where events occur.")

with st.expander("Methodology, definitions and limitations", expanded=False):
    st.markdown("""
**Source and snapshot.** NASA Open Data *Meteorite Landings*, based on Meteoritical Society records, primarily a historical snapshot through 2013. This is not the current complete inventory of recovered meteorites.

**Unit of analysis.** One database record (meteorite entry), not one independently measured atmospheric arrival event. Meteorite samples from concentrated collection regions may not reflect independent fall events.

**Cleaning.** Kept all 45,716 unique IDs. Flagged 7,315 missing positions, 6,214 placeholder (0,0) coordinates, and one invalid Earth coordinate. For the map only, omitted all 13,530 records without usable coordinates. We did not assign missing locations to continents. A suspect year (2101) is flagged; discovery year must not be interpreted as fall year for *Found* records.

**Scope.** 'Antarctic latitudes' means latitude ≤ -60°, not a legal political boundary or exact classification of every recovery expedition. The share 68.7% is **22,099 / 32,186 mappable catalog records** only. It is **not** an estimate of Antarctica's true meteorite impact share or per-area fall probability.

**Causality.** The catalog alone cannot quantify search effort or estimate the true global meteorite-fall distribution. Antarctica's preservation and concentration mechanisms are supported by external scientific literature; the data demonstrates recovery concentration, not its precise causal breakdown.

**Additional caveat.** A meteorite recorded as 'Fell' means its fall was witnessed, not that others did not fall. An entry recorded as 'Found' need not have a known fall date. The record counts also are not exposure-normalized.
""")

st.divider()
st.markdown("**Data and further reading**")
st.markdown("[NASA Open Data — Meteorite Landings](https://data.nasa.gov/dataset/meteorite-landings) · [Meteoritical Society database](https://www.lpi.usra.edu/meteor/metbull.php) · [Smithsonian Antarctic Meteorite Program](https://naturalhistory.si.edu/research/mineral-sciences/collections/meteorites/antarctic-meteorites)")
st.download_button("Download cleaned NASA meteorite records (CSV)",data=(ROOT/"meteorites_cleaned.csv").read_bytes(),file_name="meteorites_cleaned.csv",mime="text/csv")
st.caption("Built for an AUB MSBA data-storytelling assignment · Data as recorded in the historical NASA snapshot · Exploratory and educational, not a prediction of future meteorite falls.")
