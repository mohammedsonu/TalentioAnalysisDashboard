import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Talentio Analysis Dashboard", layout="wide")

st.title("Talentio Analysis Dashboard")

uploaded_file = st.file_uploader("Upload Contest Report CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    df.columns = df.columns.str.strip()
    
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participants", df['Team/User ID'].nunique())
    with col2:
        st.metric("Total Submissions", len(df))
    with col3:
        accepted_rate = (df['Result'] == 'Accepted').sum() / len(df) * 100
        st.metric("Overall Success Rate", f"{accepted_rate:.1f}%")
    with col4:
        st.metric("Total Problems", df['Problem'].nunique())
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Problem-wise Acceptance Rate")
        problem_stats = df.groupby('Problem').agg({
            'Result': lambda x: (x == 'Accepted').sum() / len(x) * 100,
            'Submission ID': 'count'
        }).reset_index()
        problem_stats.columns = ['Problem', 'Acceptance Rate', 'Total Submissions']
        
        fig = px.bar(problem_stats, x='Problem', y='Acceptance Rate', 
                     text='Acceptance Rate', color='Acceptance Rate',
                     color_continuous_scale='RdYlGn')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📈 Result Distribution")
        result_counts = df['Result'].value_counts()
        fig = px.pie(values=result_counts.values, names=result_counts.index,
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🏅 Top Performers Leaderboard")
    
    user_stats = df[df['Result'] == 'Accepted'].groupby('Team/User ID').agg({
        'Score': 'sum',
        'Problem': 'nunique',
        'Submission ID': 'count'
    }).reset_index()
    user_stats.columns = ['User ID', 'Total Score', 'Problems Solved', 'Total Submissions']
    user_stats['Efficiency'] = (user_stats['Problems Solved'] / user_stats['Total Submissions'] * 100).round(1)
    user_stats = user_stats.sort_values(['Total Score', 'Problems Solved'], ascending=False).head(10)
    
    st.dataframe(user_stats, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💻 Language Distribution")
        lang_counts = df['Language'].value_counts()
        fig = px.bar(x=lang_counts.index, y=lang_counts.values,
                     labels={'x': 'Language', 'y': 'Submissions'},
                     color=lang_counts.values, color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("✅ Success Rate by Language")
        lang_success = df.groupby('Language').agg({
            'Result': lambda x: (x == 'Accepted').sum() / len(x) * 100
        }).reset_index()
        lang_success.columns = ['Language', 'Success Rate']
        lang_success = lang_success.sort_values('Success Rate', ascending=False)
        
        fig = px.bar(lang_success, x='Language', y='Success Rate',
                     text='Success Rate', color='Success Rate',
                     color_continuous_scale='Greens')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("⚠️ Error Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        error_df = df[df['Result'] != 'Accepted']
        error_by_problem = error_df.groupby(['Problem', 'Result']).size().reset_index(name='Count')
        
        fig = px.bar(error_by_problem, x='Problem', y='Count', color='Result',
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.write("**Users with Most Errors**")
        error_users = error_df.groupby('Team/User ID').size().reset_index(name='Error Count')
        error_users = error_users.sort_values('Error Count', ascending=False).head(10)
        st.dataframe(error_users, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🔄 Multiple Attempts Analysis")
    
    attempts = df.groupby(['Team/User ID', 'Problem']).size().reset_index(name='Attempts')
    avg_attempts = attempts.groupby('Problem')['Attempts'].mean().reset_index()
    avg_attempts.columns = ['Problem', 'Average Attempts']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(avg_attempts, x='Problem', y='Average Attempts',
                     text='Average Attempts', color='Average Attempts',
                     color_continuous_scale='Reds')
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        multi_attempts = attempts[attempts['Attempts'] > 1].sort_values('Attempts', ascending=False).head(10)
        st.write("**Users with Most Attempts on Single Problem**")
        st.dataframe(multi_attempts, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🎨 User-Problem Performance Heatmap")
    
    user_problem_matrix = df.pivot_table(
        index='Team/User ID',
        columns='Problem',
        values='Result',
        aggfunc=lambda x: 1 if 'Accepted' in x.values else 0
    ).fillna(0)
    
    user_problem_matrix = user_problem_matrix.head(20)
    
    fig = px.imshow(user_problem_matrix,
                    labels=dict(x="Problem", y="User ID", color="Status"),
                    color_continuous_scale=['red', 'green'],
                    aspect="auto")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📋 Detailed Submission Data")
    
    problem_filter = st.multiselect("Filter by Problem", options=df['Problem'].unique(), default=df['Problem'].unique())
    result_filter = st.multiselect("Filter by Result", options=df['Result'].unique(), default=df['Result'].unique())
    
    filtered_df = df[(df['Problem'].isin(problem_filter)) & (df['Result'].isin(result_filter))]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    st.download_button(
        label="📥 Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_contest_data.csv',
        mime='text/csv'
    )
    
    st.markdown("---")
    
    st.subheader("📊 Score Distribution")
    fig = px.histogram(df, x='Score', nbins=20, color_discrete_sequence=['#636EFA'])
    fig.update_layout(xaxis_title="Score", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("👆 Please upload a CSV file to begin analysis")
    
    st.markdown("### Expected CSV Format:")
    st.code("""
Problem,Team/User ID,Submission ID,Language,Time,Result,Score,Status,During Contest
The Power Sum,user123,1234567,java15,1000,Accepted,20,Yes,Yes
    """)