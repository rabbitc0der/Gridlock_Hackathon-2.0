# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from sklearn.cluster import DBSCAN
# import plotly.express as px
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import roc_auc_score, classification_report
# import warnings
# warnings.filterwarnings('ignore')

# # --- CONFIGURATION ---
# st.set_page_config(layout="wide", page_title="Gridlock 2.0: Unified Intelligence", page_icon="🚦")

# # =====================================================================
# # INGEST & CLEAN
# # =====================================================================
# @st.cache_data
# def load_data():
#     df = pd.read_csv("data/theme1_clean_final.csv")
    
#     if 'created_datetime' in df.columns:
#         df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
#         if 'hour' not in df.columns:
#             df['hour'] = df['created_datetime'].dt.hour
#         if 'dow' not in df.columns:
#             df['dow'] = df['created_datetime'].dt.dayofweek
            
#     if 'primary_violation' not in df.columns:
#         df['primary_violation'] = df['violation_type'].astype(str).str.replace('"', '').str.replace('[', '').str.replace(']', '')

#     ml_df = df[df['validation_status'].isin(['approved', 'rejected'])].copy()
#     ml_df['y'] = (ml_df['validation_status'] == 'approved').astype(int) 
    
#     approved_df = df[df['validation_status'] == 'approved'].copy()
#     if 'date' not in approved_df.columns:
#         approved_df['date'] = approved_df['created_datetime'].dt.date
        
#     return df, ml_df, approved_df

# # =====================================================================
# # UNIFIED HOTSPOT REGISTRY
# # =====================================================================
# @st.cache_data
# def build_registry(approved_df):
#     named = approved_df[approved_df['junction_name'] != 'No Junction'].dropna(subset=['latitude', 'longitude']).copy()
#     named_stats = named.groupby('junction_name').agg(
#         total_violations=('id', 'count'),
#         unique_devices=('device_id', 'nunique'),
#         active_days=('date', 'nunique'),
#         latitude=('latitude', 'mean'),
#         longitude=('longitude', 'mean')
#     ).reset_index().rename(columns={'junction_name': 'zone_id'})
#     named_stats['zone_type'] = 'named_junction'

#     no_junction = approved_df[approved_df['junction_name'] == 'No Junction'].dropna(subset=['latitude', 'longitude']).copy()
#     coords = no_junction[['latitude', 'longitude']].values
    
#     db = DBSCAN(eps=0.00045, min_samples=20).fit(coords)
#     no_junction['cluster_id'] = db.labels_
    
#     discovered = no_junction[no_junction['cluster_id'] != -1].copy()
#     discovered['zone_id'] = 'Discovered_Zone_' + discovered['cluster_id'].astype(str)
    
#     discovered_stats = discovered.groupby('zone_id').agg(
#         total_violations=('id', 'count'),
#         unique_devices=('device_id', 'nunique'),
#         active_days=('date', 'nunique'),
#         latitude=('latitude', 'mean'),
#         longitude=('longitude', 'mean')
#     ).reset_index()
#     discovered_stats['zone_type'] = 'discovered_cluster'

#     registry = pd.concat([named_stats, discovered_stats], ignore_index=True)
#     registry['active_days'] = registry['active_days'].replace(0, 1)
#     registry['daily_avg'] = registry['total_violations'] / registry['active_days']
    
#     return registry, no_junction

# # =====================================================================
# # PRESSURE INDEX & SENSITIVITY CHECK
# # =====================================================================
# def compute_pressure(reg, w):
#     r = reg.copy()
#     r['norm_vol'] = r['total_violations'] / r['total_violations'].max()
#     r['norm_days'] = r['active_days'] / r['active_days'].max()
#     r['norm_dev'] = r['unique_devices'] / r['unique_devices'].max()
#     r['pressure'] = w[0]*r['norm_vol'] + w[1]*r['norm_days'] + w[2]*r['norm_dev']
#     return r

# # =====================================================================
# # RECOMMENDATION ENGINE HELPERS
# # =====================================================================
# def zone_profile(source_df, no_junc_df, zone_value):
#     if str(zone_value).startswith('Discovered_Zone_'):
#         cluster_id = int(str(zone_value).split('_')[-1])
#         rows = no_junc_df[no_junc_df['cluster_id'] == cluster_id]
#     else:
#         rows = source_df[source_df['junction_name'] == zone_value]
        
#     top_vehicle = rows['vehicle_type'].value_counts().idxmax() if len(rows) else 'Unknown'
#     top_violation = rows['primary_violation'].value_counts().idxmax() if len(rows) else 'Unknown'
#     peak_hour = rows['hour'].value_counts().idxmax() if len(rows) else 0
#     return top_vehicle, top_violation, peak_hour

# def zone_recommendation(zone_id, vehicle, violation, peak_hour, daily_avg):
#     return (f"**Zone {zone_id}**: Deploy {vehicle.lower()}-focused enforcement, "
#             f"targeting {violation.lower()}, peak window {peak_hour}:00–{(peak_hour+2)%24}:00. "
#             f"Daily pressure: {daily_avg:.1f} violations/day.")

# def device_recommendation(device_id, rejection_rate, total_flags):
#     return (f"**Device {device_id}**: {rejection_rate:.1%} rejection rate over {total_flags} flags. "
#             f"Recommend physical inspection/recalibration.")

# # --- INITIALIZATION ---
# with st.spinner("Loading ASTraM Core Systems..."):
#     df_full, ml_df, approved_df = load_data()
#     raw_registry, no_junc_df = build_registry(approved_df)
    
#     weight_sets = {'current': (0.5, 0.3, 0.2), 'equal': (1/3, 1/3, 1/3), 'inverted': (0.2, 0.3, 0.5)}
#     top10 = {}
#     for name, w in weight_sets.items():
#         scored = compute_pressure(raw_registry, w)
#         top10[name] = set(scored.sort_values('pressure', ascending=False).head(10)['zone_id'])
#     stable = top10['current'] & top10['equal'] & top10['inverted']
#     stability_count = len(stable)
    
#     registry = compute_pressure(raw_registry, weight_sets['current'])
#     registry = registry.sort_values('pressure', ascending=False).reset_index(drop=True)

# # =====================================================================
# # DASHBOARD UI ROUTING
# # =====================================================================
# st.sidebar.title("🚦 Gridlock 2.0")
# st.sidebar.markdown("**Unified Intelligence**")
# page = st.sidebar.radio("Navigation", [
#     "🗺️ Hotspot Command Center", 
#     "🛠️ Camera Reliability Audit"
# ])

# if page == "🗺️ Hotspot Command Center":
#     st.title("🗺️ Unified Hotspot Command Center")
#     st.markdown("Prioritizing enforcement across known junctions and undocumented AI-discovered clusters.")
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Validated Violations", f"{len(approved_df):,}")
#     col2.metric("Named Junctions Tracked", len(registry[registry['zone_type'] == 'named_junction']))
#     col3.metric("Hidden Hotspots Discovered", len(registry[registry['zone_type'] == 'discovered_cluster']))
#     col4.success(f"**Robustness:** Top 10 stable across 3 weighting schemes ({stability_count}/10)")

#     st.markdown("---")
    
#     st.subheader("Global Hotspot Map")
#     st.caption("🔵 Named Junctions | 🔴 Discovered DBSCAN Clusters")
#     m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="CartoDB positron")
#     for _, row in registry.head(75).iterrows():
#         color = "blue" if row['zone_type'] == 'named_junction' else "red"
#         folium.CircleMarker(
#             location=[row['latitude'], row['longitude']],
#             radius=5 + (row['pressure'] * 8), 
#             popup=f"{row['zone_id']} (Avg: {row['daily_avg']:.1f}/day)",
#             color=color, fill=True, fill_opacity=0.7
#         ).add_to(m)
#     st_folium(m, width=1400, height=450, returned_objects=[])

#     st.markdown("---")
    
#     st.subheader("Temporal Enforcement Vacuum")
#     st.caption("Proving the 2 PM enforcement drop-off (IST)")
#     heat_data = approved_df.groupby(['dow', 'hour']).size().reset_index(name='violation_count')
#     day_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
#     heat_data['Day'] = heat_data['dow'].map(day_map)
#     fig = px.density_heatmap(
#         heat_data, x="hour", y="Day", z="violation_count", 
#         color_continuous_scale="Reds",
#         labels={'hour': 'Hour (IST)', 'Day': 'Day', 'violation_count': 'Violations'}
#     )
#     fig.update_traces(xgap=1, ygap=1)
#     fig.update_layout(
#         margin=dict(l=0, r=0, t=0, b=0), 
#         height=400,
#         plot_bgcolor='black'
#     )
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     st.subheader("Unified Pressure Registry (Top 20)")
#     st.info("💡 **Methodology Note:** The Pressure Index is a frequency, persistence, and device-coverage based proxy for parking-induced congestion impact. No direct traffic-speed or road-network telemetry was available in the provided dataset.")
    
#     st.dataframe(
#         registry[['zone_id', 'zone_type', 'daily_avg', 'pressure']].head(20).style.format({"daily_avg": "{:.1f}", "pressure": "{:.3f}"}),
#         use_container_width=True
#     )
    
#     # Export clean data without intermediate math columns
#     export_cols = ['zone_id', 'zone_type', 'total_violations', 'unique_devices', 'active_days', 'daily_avg', 'pressure']
#     clean_registry = registry[export_cols]
    
#     st.download_button(
#         label="📥 Download Complete Registry (CSV)",
#         data=clean_registry.to_csv(index=False).encode('utf-8'),
#         file_name="unified_pressure_registry.csv",
#         mime="text/csv",
#     )
    
#     st.markdown("---")
#     st.subheader("Actionable Directives")
#     selected_zone = st.selectbox("Select Zone for Field Directive:", registry['zone_id'].head(50))
#     if selected_zone:
#         zone_data = registry[registry['zone_id'] == selected_zone].iloc[0]
#         top_v, top_viol, p_hour = zone_profile(approved_df, no_junc_df, selected_zone)
#         st.success(zone_recommendation(selected_zone, top_v, top_viol, p_hour, zone_data['daily_avg']))

# # =====================================================================
# # CAMERA RELIABILITY CLASSIFIER
# # =====================================================================
# elif page == "🛠️ Camera Reliability Audit":
#     st.title("🛠️ Camera Reliability Classifier")
#     st.markdown("Target-encoded ML architecture to isolate hardware faults based on historical human-reviewer patterns.")
    
#     with st.spinner("Training target-encoded Random Forest..."):
#         cat_cols = ['device_id', 'vehicle_type', 'primary_violation', 'junction_name', 'police_station']
#         for c in cat_cols:
#             ml_df[c] = ml_df[c].fillna('Unknown')
            
#         train, test = train_test_split(ml_df, test_size=0.2, random_state=42, stratify=ml_df['y'])
#         encoders = {c: LabelEncoder().fit(ml_df[c].astype(str)) for c in cat_cols}

#         train_dev_stats = train.groupby('device_id')['y'].agg(['mean', 'count'])
#         default_rate = train['y'].mean()

#         def encode(d):
#             out = pd.DataFrame(index=d.index)
#             out['device_encoded'] = encoders['device_id'].transform(d['device_id'].astype(str))
#             out['vehicle_encoded'] = encoders['vehicle_type'].transform(d['vehicle_type'].astype(str))
#             out['violation_encoded'] = encoders['primary_violation'].transform(d['primary_violation'].astype(str))
#             out['junction_encoded'] = encoders['junction_name'].transform(d['junction_name'].astype(str))
#             out['station_encoded'] = encoders['police_station'].transform(d['police_station'].astype(str))
#             out['hour'] = d['hour']
#             out['dow'] = d['dow']
#             out['device_hist_approve_rate'] = d['device_id'].map(train_dev_stats['mean']).fillna(default_rate)
#             out['device_train_volume'] = d['device_id'].map(train_dev_stats['count']).fillna(0)
#             return out

#         X_train, X_test = encode(train), encode(test)
#         y_train, y_test = train['y'], test['y']

#         clf = RandomForestClassifier(n_estimators=150, max_depth=18, class_weight='balanced', random_state=42, n_jobs=-1)
#         clf.fit(X_train, y_train)
        
#         proba = clf.predict_proba(X_test)
#         auc = roc_auc_score(y_test, proba[:, 1])
#         preds = clf.predict(X_test)
#         report = classification_report(y_test, preds, output_dict=True)

#     st.markdown("### Model Validation Metrics")
#     m1, m2, m3, m4 = st.columns(4)
#     m1.metric("Model AUC", f"{auc:.3f}")
#     m2.metric("Rejected-Class F1", f"{report['0']['f1-score']:.3f}")
#     m3.metric("Recall", f"{report['0']['recall']:.3f}")
#     m4.metric("Precision", f"{report['0']['precision']:.3f}")
    
#     st.info("💡 **Honest Ceiling:** The model is designed to prioritize devices for human inspection, not fully automate the approve/reject decision, since the photo evidence that drives the final human decision isn't present in this dataset.")
#     st.caption(f"*Baseline Majority-Class Accuracy Context:* `{default_rate:.2%}`")

#     st.markdown("---")
    
#     st.subheader("Hardware Flag Registry")
    
#     device_audit = ml_df.groupby('device_id').agg(
#         total_flags=('y', 'count'),
#         rejections=('y', lambda x: (x == 0).sum())
#     ).reset_index()
#     device_audit['rejection_rate'] = device_audit['rejections'] / device_audit['total_flags']
#     faulty_cameras = device_audit[(device_audit['total_flags'] > 50) & (device_audit['rejection_rate'] > 0.60)]
#     faulty_cameras = faulty_cameras.sort_values('rejection_rate', ascending=False)

#     col_t, col_r = st.columns([1, 1.2])
#     with col_t:
#         st.dataframe(faulty_cameras.head(20).style.format({"rejection_rate": "{:.1%}"}), use_container_width=True, height=400)
        
#         st.download_button(
#             label="📥 Download Complete Hardware Audit (CSV)",
#             data=faulty_cameras.to_csv(index=False).encode('utf-8'),
#             file_name="hardware_audit_registry.csv",
#             mime="text/csv",
#         )
        
#     with col_r:
#         st.markdown("#### Device Directives")
#         sel_dev = st.selectbox("Select Device for Review:", faulty_cameras['device_id'].head(20))
#         if sel_dev:
#             d_row = faulty_cameras[faulty_cameras['device_id'] == sel_dev].iloc[0]
#             st.warning(device_recommendation(sel_dev, d_row['rejection_rate'], d_row['total_flags']))

import streamlit as st
import pandas as pd
import numpy as np
import folium
import os
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Gridlock 2.0: Unified Intelligence", page_icon="🚦")

# =====================================================================
# ROBUST DATA INGESTION
# =====================================================================
@st.cache_data
def load_data():
    # Looks for the file in multiple potential path variations to avoid case-sensitivity crashes
    paths = ["data/theme1_clean_final.csv", "Data/theme1_clean_final.csv", "theme1_clean_final.csv"]
    file_path = next((p for p in paths if os.path.exists(p)), None)
    
    if not file_path:
        st.error(f"FATAL ERROR: Could not find theme1_clean_final.csv. Current directory structure: {os.listdir()}")
        st.stop()
        
    df = pd.read_csv(file_path)
    
    if 'created_datetime' in df.columns:
        df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
        if 'hour' not in df.columns:
            df['hour'] = df['created_datetime'].dt.hour
        if 'dow' not in df.columns:
            df['dow'] = df['created_datetime'].dt.dayofweek
            
    if 'primary_violation' not in df.columns:
        df['primary_violation'] = df['violation_type'].astype(str).str.replace('"', '').str.replace('[', '').str.replace(']', '')

    ml_df = df[df['validation_status'].isin(['approved', 'rejected'])].copy()
    ml_df['y'] = (ml_df['validation_status'] == 'approved').astype(int) 
    
    approved_df = df[df['validation_status'] == 'approved'].copy()
    if 'date' not in approved_df.columns:
        approved_df['date'] = approved_df['created_datetime'].dt.date
        
    return df, ml_df, approved_df

# =====================================================================
# REGISTRY & ANALYTICS FUNCTIONS
# =====================================================================
@st.cache_data
def build_registry(approved_df):
    named = approved_df[approved_df['junction_name'] != 'No Junction'].dropna(subset=['latitude', 'longitude']).copy()
    named_stats = named.groupby('junction_name').agg(
        total_violations=('id', 'count'),
        unique_devices=('device_id', 'nunique'),
        active_days=('date', 'nunique'),
        latitude=('latitude', 'mean'),
        longitude=('longitude', 'mean')
    ).reset_index().rename(columns={'junction_name': 'zone_id'})
    named_stats['zone_type'] = 'named_junction'

    no_junction = approved_df[approved_df['junction_name'] == 'No Junction'].dropna(subset=['latitude', 'longitude']).copy()
    coords = no_junction[['latitude', 'longitude']].values
    
    db = DBSCAN(eps=0.00045, min_samples=20).fit(coords)
    no_junction['cluster_id'] = db.labels_
    
    discovered = no_junction[no_junction['cluster_id'] != -1].copy()
    discovered['zone_id'] = 'Discovered_Zone_' + discovered['cluster_id'].astype(str)
    
    discovered_stats = discovered.groupby('zone_id').agg(
        total_violations=('id', 'count'),
        unique_devices=('device_id', 'nunique'),
        active_days=('date', 'nunique'),
        latitude=('latitude', 'mean'),
        longitude=('longitude', 'mean')
    ).reset_index()
    discovered_stats['zone_type'] = 'discovered_cluster'

    registry = pd.concat([named_stats, discovered_stats], ignore_index=True)
    registry['active_days'] = registry['active_days'].replace(0, 1)
    registry['daily_avg'] = registry['total_violations'] / registry['active_days']
    
    return registry, no_junction

def compute_pressure(reg, w):
    r = reg.copy()
    r['norm_vol'] = r['total_violations'] / r['total_violations'].max()
    r['norm_days'] = r['active_days'] / r['active_days'].max()
    r['norm_dev'] = r['unique_devices'] / r['unique_devices'].max()
    r['pressure'] = w[0]*r['norm_vol'] + w[1]*r['norm_days'] + w[2]*r['norm_dev']
    return r

def zone_profile(source_df, no_junc_df, zone_value):
    if str(zone_value).startswith('Discovered_Zone_'):
        cluster_id = int(str(zone_value).split('_')[-1])
        rows = no_junc_df[no_junc_df['cluster_id'] == cluster_id]
    else:
        rows = source_df[source_df['junction_name'] == zone_value]
        
    top_vehicle = rows['vehicle_type'].value_counts().idxmax() if len(rows) else 'Unknown'
    top_violation = rows['primary_violation'].value_counts().idxmax() if len(rows) else 'Unknown'
    peak_hour = rows['hour'].value_counts().idxmax() if len(rows) else 0
    return top_vehicle, top_violation, peak_hour

def zone_recommendation(zone_id, vehicle, violation, peak_hour, daily_avg):
    return (f"**Zone {zone_id}**: Deploy {vehicle.lower()}-focused enforcement, "
            f"targeting {violation.lower()}, peak window {peak_hour}:00–{(peak_hour+2)%24}:00. "
            f"Daily pressure: {daily_avg:.1f} violations/day.")

def device_recommendation(device_id, rejection_rate, total_flags):
    return (f"**Device {device_id}**: {rejection_rate:.1%} rejection rate over {total_flags} flags. "
            f"Recommend physical inspection/recalibration.")

# --- INITIALIZATION ---
with st.spinner("Loading ASTraM Core Systems..."):
    df_full, ml_df, approved_df = load_data()
    raw_registry, no_junc_df = build_registry(approved_df)
    
    weight_sets = {'current': (0.5, 0.3, 0.2), 'equal': (1/3, 1/3, 1/3), 'inverted': (0.2, 0.3, 0.5)}
    top10 = {}
    for name, w in weight_sets.items():
        scored = compute_pressure(raw_registry, w)
        top10[name] = set(scored.sort_values('pressure', ascending=False).head(10)['zone_id'])
    stable = top10['current'] & top10['equal'] & top10['inverted']
    stability_count = len(stable)
    
    registry = compute_pressure(raw_registry, weight_sets['current'])
    registry = registry.sort_values('pressure', ascending=False).reset_index(drop=True)

# =====================================================================
# DASHBOARD UI ROUTING
# =====================================================================
st.sidebar.title("🚦 Gridlock 2.0")
st.sidebar.markdown("**Unified Intelligence**")
page = st.sidebar.radio("Navigation", [
    "🗺️ Hotspot Command Center", 
    "🛠️ Camera Reliability Audit"
])

if page == "🗺️ Hotspot Command Center":
    st.title("🗺️ Unified Hotspot Command Center")
    st.markdown("Prioritizing enforcement across known junctions and undocumented AI-discovered clusters.")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Validated Violations", f"{len(approved_df):,}")
    col2.metric("Named Junctions Tracked", len(registry[registry['zone_type'] == 'named_junction']))
    col3.metric("Hidden Hotspots Discovered", len(registry[registry['zone_type'] == 'discovered_cluster']))
    col4.success(f"**Robustness:** Top 10 stable across 3 weighting schemes ({stability_count}/10)")

    st.markdown("---")
    
    st.subheader("Global Hotspot Map")
    st.caption("🔵 Named Junctions | 🔴 Discovered DBSCAN Clusters")
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="CartoDB positron")
    for _, row in registry.head(75).iterrows():
        color = "blue" if row['zone_type'] == 'named_junction' else "red"
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5 + (row['pressure'] * 8), 
            popup=f"{row['zone_id']} (Avg: {row['daily_avg']:.1f}/day)",
            color=color, fill=True, fill_opacity=0.7
        ).add_to(m)
    st_folium(m, width=1400, height=450, returned_objects=[])

    st.markdown("---")
    
    st.subheader("Temporal Enforcement Vacuum")
    st.caption("Proving the 2 PM enforcement drop-off (IST)")
    heat_data = approved_df.groupby(['dow', 'hour']).size().reset_index(name='violation_count')
    day_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
    heat_data['Day'] = heat_data['dow'].map(day_map)
    fig = px.density_heatmap(
        heat_data, x="hour", y="Day", z="violation_count", 
        color_continuous_scale="Reds",
        labels={'hour': 'Hour (IST)', 'Day': 'Day', 'violation_count': 'Violations'}
    )
    fig.update_traces(xgap=1, ygap=1)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400, plot_bgcolor='black')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Unified Pressure Registry (Top 20)")
    st.info("💡 **Methodology Note:** The Pressure Index is a frequency, persistence, and device-coverage based proxy for parking-induced congestion impact.")
    
    st.dataframe(
        registry[['zone_id', 'zone_type', 'daily_avg', 'pressure']].head(20).style.format({"daily_avg": "{:.1f}", "pressure": "{:.3f}"}),
        use_container_width=True
    )
    
    export_cols = ['zone_id', 'zone_type', 'total_violations', 'unique_devices', 'active_days', 'daily_avg', 'pressure']
    clean_registry = registry[export_cols]
    
    st.download_button(
        label="📥 Download Complete Registry (CSV)",
        data=clean_registry.to_csv(index=False).encode('utf-8'),
        file_name="unified_pressure_registry.csv",
        mime="text/csv",
    )
    
    st.markdown("---")
    st.subheader("Actionable Directives")
    selected_zone = st.selectbox("Select Zone for Field Directive:", registry['zone_id'].head(50))
    if selected_zone:
        zone_data = registry[registry['zone_id'] == selected_zone].iloc[0]
        top_v, top_viol, p_hour = zone_profile(approved_df, no_junc_df, selected_zone)
        st.success(zone_recommendation(selected_zone, top_v, top_viol, p_hour, zone_data['daily_avg']))

# =====================================================================
# CAMERA RELIABILITY CLASSIFIER
# =====================================================================
elif page == "🛠️ Camera Reliability Audit":
    st.title("🛠️ Camera Reliability Classifier")
    st.markdown("Target-encoded ML architecture to isolate hardware faults based on historical human-reviewer patterns.")
    
    with st.spinner("Training target-encoded Random Forest..."):
        cat_cols = ['device_id', 'vehicle_type', 'primary_violation', 'junction_name', 'police_station']
        for c in cat_cols:
            ml_df[c] = ml_df[c].fillna('Unknown')
            
        train, test = train_test_split(ml_df, test_size=0.2, random_state=42, stratify=ml_df['y'])
        encoders = {c: LabelEncoder().fit(ml_df[c].astype(str)) for c in cat_cols}

        train_dev_stats = train.groupby('device_id')['y'].agg(['mean', 'count'])
        default_rate = train['y'].mean()

        def encode(d):
            out = pd.DataFrame(index=d.index)
            out['device_encoded'] = encoders['device_id'].transform(d['device_id'].astype(str))
            out['vehicle_encoded'] = encoders['vehicle_type'].transform(d['vehicle_type'].astype(str))
            out['violation_encoded'] = encoders['primary_violation'].transform(d['primary_violation'].astype(str))
            out['junction_encoded'] = encoders['junction_name'].transform(d['junction_name'].astype(str))
            out['station_encoded'] = encoders['police_station'].transform(d['police_station'].astype(str))
            out['hour'] = d['hour']
            out['dow'] = d['dow']
            out['device_hist_approve_rate'] = d['device_id'].map(train_dev_stats['mean']).fillna(default_rate)
            out['device_train_volume'] = d['device_id'].map(train_dev_stats['count']).fillna(0)
            return out

        X_train, X_test = encode(train), encode(test)
        y_train, y_test = train['y'], test['y']

        clf = RandomForestClassifier(n_estimators=150, max_depth=18, class_weight='balanced', random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)
        
        proba = clf.predict_proba(X_test)
        auc = roc_auc_score(y_test, proba[:, 1])
        preds = clf.predict(X_test)
        report = classification_report(y_test, preds, output_dict=True)

    st.markdown("### Model Validation Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model AUC", f"{auc:.3f}")
    m2.metric("Rejected-Class F1", f"{report['0']['f1-score']:.3f}")
    m3.metric("Recall", f"{report['0']['recall']:.3f}")
    m4.metric("Precision", f"{report['0']['precision']:.3f}")
    
    st.info("💡 **Honest Ceiling:** The model acts as a triage layer, flagging high-rejection devices for manual inspection.")
    st.caption(f"*Baseline Majority-Class Accuracy Context:* `{default_rate:.2%}`")

    st.markdown("---")
    
    st.subheader("Hardware Flag Registry")
    
    device_audit = ml_df.groupby('device_id').agg(
        total_flags=('y', 'count'),
        rejections=('y', lambda x: (x == 0).sum())
    ).reset_index()
    device_audit['rejection_rate'] = device_audit['rejections'] / device_audit['total_flags']
    faulty_cameras = device_audit[(device_audit['total_flags'] > 50) & (device_audit['rejection_rate'] > 0.60)]
    faulty_cameras = faulty_cameras.sort_values('rejection_rate', ascending=False)

    col_t, col_r = st.columns([1, 1.2])
    with col_t:
        st.dataframe(faulty_cameras.head(20).style.format({"rejection_rate": "{:.1%}"}), use_container_width=True, height=400)
        st.download_button(
            label="📥 Download Complete Hardware Audit (CSV)",
            data=faulty_cameras.to_csv(index=False).encode('utf-8'),
            file_name="hardware_audit_registry.csv",
            mime="text/csv",
        )
        
    with col_r:
        st.markdown("#### Device Directives")
        sel_dev = st.selectbox("Select Device for Review:", faulty_cameras['device_id'].head(20))
        if sel_dev:
            d_row = faulty_cameras[faulty_cameras['device_id'] == sel_dev].iloc[0]
            st.warning(device_recommendation(sel_dev, d_row['rejection_rate'], d_row['total_flags']))