import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# Show app title and description.
st.set_page_config(page_title="Tasks", page_icon="🎫")
st.title("🎫 Add Task")
st.write(
    """
    This app manage my tasks.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    issue_descriptions = [
        "Math Homework",
        "English Essay",
        "Physics Home work",
        "Complete homework", "Attend meeting", "Buy groceries", "Prepare for test", 
    "Organize event", "Study for exam", "Clean the house", "Practice coding", 
    "Complete project", "Finish reading book",
    ]

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"TASK-{i}" for i in range(1100, 1100 - 100, -1)],  # TASK-1100 to TASK-1001
        "Task": np.random.choice(issue_descriptions, size=100),
        "Category": np.random.choice(["Academic", "Co-curricular", "Personal", "Other"], size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Due Date": [
            (datetime.date(2025, 2, 22) + datetime.timedelta(days=random.randint(0, 182)))  # Fixing the issue with the 'Due Date'
            for _ in range(100)
        ],
        "Date Submitted": [None for _ in range(100)],  # Placeholder
    }
    # Now, populate the "Date Submitted" such that it is before the "Due Date"
    for i in range(100):
        due_date = data["Due Date"][i]
        # Generate Date Submitted to be before Due Date
        date_submitted = datetime.date(2025, 2, 15) + datetime.timedelta(days=random.randint(0, (due_date - datetime.date(2025, 2, 15)).days))
        data["Date Submitted"][i] = date_submitted

    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across page runs).
    st.session_state.df = df
    


# Show a section to add a new ticket.
st.header("Add a Task")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_task_form"):
    issue = st.text_area("Describe the task")
    category= st.selectbox("Category", ["Academic", "Co-curricular", "Personal", "Other"])
    due_date = st.date_input("Due Date")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TASK-{recent_ticket_number+1}",
                "Issue": issue,
                "Category": category,
                "Status": "Open",
                "Priority": priority,
                "Due Date": due_date,
                "Date Submitted": today,
                
            }
        ]
    )

    # Show a little success message.
    st.write("Task created! Here are your task priority list:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table.
st.header("Existing Tasks")
st.write(f"Number of Tasks: `{len(st.session_state.df)}`")

st.info(
    "You can edit the task by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show a chart of task priorities for each category
st.header("Task Priorities by Category")

# Create 4 columns for displaying each pie chart
col1, col2, col3, col4 = st.columns(4)

# List of categories
categories = st.session_state.df["Category"].unique()

# Loop over each category and display a pie chart for task priorities in that category
for i, category in enumerate(categories):
    category_df = st.session_state.df[st.session_state.df["Category"] == category]
    
    # Pie chart for the priority distribution in this category (without legend)
    priority_plot = (
        alt.Chart(category_df)
        .mark_arc()
        .encode(
            theta="count():Q",  # Count the number of tasks per priority
            color=alt.Color("Priority:N", legend=None),  # Disable legend for this individual pie chart
            tooltip=["Priority:N", "count():Q"]  # Show priority and count in the tooltip
        )
        .properties(title=f"Task for {category}")
    )

    # Display each chart in a separate column
    if i == 0:
        col1.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
    elif i == 1:
        col2.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
    elif i == 2:
        col3.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
    else:
        col4.altair_chart(priority_plot, use_container_width=True, theme="streamlit")

# Display a combined pie chart for legend display below the graphs
st.write("##### Task Priorities Combined (for Legend)")
priority_combined_plot = (
    alt.Chart(st.session_state.df)
    .mark_arc()
    .encode(
        theta="count():Q",  # Count the number of tasks per priority
        color=alt.Color("Priority:N"),  # Enable legend for the combined chart
        tooltip=["Priority:N", "count():Q"]  # Show priority and count in the tooltip
    )
    .properties(height=200)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)

# Display the combined pie chart with legend below
st.altair_chart(priority_combined_plot, use_container_width=True, theme="streamlit")

# Show a chart of task status for each category
st.header("Task Status by Category")

# Create 4 columns for displaying each pie chart
col1, col2, col3, col4 = st.columns(4)

# List of categories
categories = st.session_state.df["Category"].unique()

# Pie chart size to ensure consistency
chart_width = 200
chart_height = 200

# Loop over each category and display a pie chart for task status in that category
for i, category in enumerate(categories):
    category_df = st.session_state.df[st.session_state.df["Category"] == category]
    
    # Pie chart for the status distribution in this category (without legend)
    status_plot = (
        alt.Chart(category_df)
        .mark_arc()
        .encode(
            theta="count():Q",  # Count the number of tasks per status
            color=alt.Color("Status:N", legend=None),  # Disable legend for this individual pie chart
            tooltip=["Status:N", "count():Q"]  # Show status and count in the tooltip
        )
        .properties(width=chart_width, height=chart_height, title=f"Task Status for {category}")  # Set the same size for all charts
    )

    # Display each chart in a separate column
    if i == 0:
        col1.altair_chart(status_plot, use_container_width=True, theme="streamlit")
    elif i == 1:
        col2.altair_chart(status_plot, use_container_width=True, theme="streamlit")
    elif i == 2:
        col3.altair_chart(status_plot, use_container_width=True, theme="streamlit")
    else:
        col4.altair_chart(status_plot, use_container_width=True, theme="streamlit")

# Display a combined pie chart for legend display below the graphs
st.write("##### Task Status Combined (for Legend)")
status_combined_plot = (
    alt.Chart(st.session_state.df)
    .mark_arc()
    .encode(
        theta="count():Q",  # Count the number of tasks per status
        color=alt.Color("Status:N"),  # Enable legend for the combined chart
        tooltip=["Status:N", "count():Q"]  # Show status and count in the tooltip
    )
    .properties(height=200)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)

# Display the combined pie chart with legend below
st.altair_chart(status_combined_plot, use_container_width=True, theme="streamlit")
