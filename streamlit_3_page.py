import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load the data and merge it
@st.cache_data
def load_data():
    death_penalty_df = pd.read_excel('death_penalty_2024.xlsx', sheet_name='CDPD version 1 June 2024 (7)')
    cow2iso_df = pd.read_csv('cow2iso.csv')
    # Ensure both 'COWCODE' and 'cowcode' are integers
    death_penalty_df['COWCODE'] = death_penalty_df['COWCODE'].astype(int)
    cow2iso_df['cowcode'] = cow2iso_df['cowcode'].astype(int)
    # Merge death penalty data with cow2iso to get ISO3 codes
    merged_df = death_penalty_df.merge(cow2iso_df[['cowcode', 'Iso3']], left_on='COWCODE', right_on='cowcode', how='left')
    return merged_df

# Load the data
merged_df_final = load_data()

# Filter data for the selected year
def filter_data_by_year(df, year):
    return df[df['Year'] == year]

# Filter data for the number of countries that have not abolished the death penalty (deathpenalty > 0)
def count_countries_not_abolished(df):
    return df[df['Deathpenalty'] > 0].groupby('Year').size().reset_index(name='Number of Countries')

# Main Streamlit app
def time_series_and_bar():
    st.subheader('Global Death Penalty Statistics (1924 - 2024)')

    # Filter and count countries that have not abolished the death penalty (DeathPenalty > 0)
    time_series_data = count_countries_not_abolished(merged_df_final)

    # Filter for the last 100 years (1924-2024)
    time_series_data = time_series_data[(time_series_data['Year'] >= 1924) & (time_series_data['Year'] <= 2024)]

    # Plot the time-series line chart
    fig = px.line(
        time_series_data,
        x='Year',
        y='Number of Countries',
        title="Number of Countries That Have Not Abolished the Death Penalty (1924 - 2024)",
        labels={'Number of Countries': 'Countries with Death Penalty'}
    )

    # Second Visualization: Bar chart for Death Penalty Distribution in 2024
    #st.subheader("Death Penalty Distribution in 2024")
    latest_year = merged_df_final['Year'].max()
    year_2024_data = filter_data_by_year(merged_df_final, latest_year)

    # Plot the bar chart
    fig_bar = px.bar(
        year_2024_data.groupby('Deathpenalty').size().reset_index(name='Country Count'),
        x='Deathpenalty',
        y='Country Count',
        title=f'Distribution of Death Penalty Status in {latest_year}',
        labels={'Deathpenalty': 'Death Penalty Status', 'Country Count': 'Number of Countries'}
    )

    # Display the time-series and bar chart side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig)
    with col2:
        st.plotly_chart(fig_bar)

    # Original description restored below the charts
    st.markdown("""
    **Note**:  
    The line chart displays the number of countries that have not abolished the death penalty from 1924 to 2024. 
    The bar chart shows the distribution of death penalty status in 2024 as:
    - **0 = Abolished**: The death penalty has been fully abolished.
    - **1 = Abolished for ordinary crimes only**: The death penalty is only abolished for ordinary crimes.
    - **2 = Abolished for ordinary crimes only, but used during the last 10 years**: The death penalty is abolished for ordinary crimes, but has been used in the last 10 years.
    - **3 = Abolished in practice**: The death penalty is not actively used, but still legally exists.
    - **4 = Retained**: The death penalty is still fully retained and used.
    """)


def global_map():
    st.subheader('Global Death Penalty Status Map')

    # Dropdown for selecting years in increments of 10
    selected_year = st.selectbox('Select Year', [i for i in range(1950, 2021, 10)])

    # Filter the data for the selected year
    filtered_data = filter_data_by_year(merged_df_final, selected_year)

    # Plot the map using Plotly
    fig = px.choropleth(
        filtered_data,
        locations='Iso3',
        locationmode='ISO-3',
        color='Deathpenalty',
        hover_name='Country',
        color_continuous_scale='ylorrd',
        range_color=(0, 4),
        labels={'Deathpenalty': 'Death Penalty Status'},
        title=f"Global Death Penalty Status in {selected_year}"
    )

    fig.update_layout(
        height=600,
        width=1000,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
    )

    # Display the figure
    st.plotly_chart(fig)

    # Explanation of Death Penalty values
    st.markdown("""
    **Death Penalty Status Values:**

    - **0 = Abolished**: The death penalty has been fully abolished.
    - **1 = Abolished for ordinary crimes only**: The death penalty is only abolished for ordinary crimes.
    - **2 = Abolished for ordinary crimes only, but used during the last 10 years**: The death penalty is abolished for ordinary crimes, but has been used in the last 10 years.
    - **3 = Abolished in practice**: The death penalty is not actively used, but still legally exists.
    - **4 = Retained**: The death penalty is still fully retained and used.
    """)


def status_comparison():
    st.subheader("Trends in Death Penalty Policies Over Time")

    # Create a meaningful third visualization: Changes in Death Penalty status over time
    death_penalty_changes = merged_df_final.groupby(['Year', 'Deathpenalty']).size().reset_index(name='Change Count')

    # Plotting changes in death penalty status over time
    fig_changes = px.line(
        death_penalty_changes,
        x='Year',
        y='Change Count',
        color='Deathpenalty',
        title="Trends in Death Penalty Policies Over Time",
        labels={'Change Count': 'Frequency of Status Changes', 'Deathpenalty': 'Death Penalty Status'}
    )

    fig_changes.update_layout(
        height=600,
        width=1000,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
    )

    # Display the third visualization
    st.plotly_chart(fig_changes)

    # Description for Page 3
    # Explanation of Death Penalty values
    st.markdown("""
    The chart above shows how the death penalty status has changed over time across various countries.
    **Death Penalty Status Values:**

    - **0 = Abolished**: The death penalty has been fully abolished.
    - **1 = Abolished for ordinary crimes only**: The death penalty is only abolished for ordinary crimes.
    - **2 = Abolished for ordinary crimes only, but used during the last 10 years**: The death penalty is abolished for ordinary crimes, but has been used in the last 10 years.
    - **3 = Abolished in practice**: The death penalty is not actively used, but still legally exists.
    - **4 = Retained**: The death penalty is still fully retained and used.
    """)


# Navigation Logic at the END
def main():
    st.sidebar.title('Death Penalty Data Visuals')
    page = st.sidebar.radio('Go to', ['Time-Series Chart and Bar', 'Global Map', 'Status Comparison'])

    if page == 'Time-Series Chart and Bar':
        time_series_and_bar()
    elif page == 'Global Map':
        global_map()
    elif page == 'Status Comparison':
        status_comparison()


if __name__ == "__main__":
    main()

