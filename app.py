import streamlit as st
import os
from ai_agent import TaskAgent

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AI Task Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Task Agent with SQLite Brain")
    st.markdown("Manage your tasks using natural language!")
    
    # API Key setup
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("🔑 Please set your OPENAI_API_KEY environment variable")
        st.code("export OPENAI_API_KEY=your_key_here")
        return
    
    # Initialize the AI agent
    if 'agent' not in st.session_state:
        st.session_state.agent = TaskAgent(api_key)
    
    # Chat interface
    st.subheader("💬 Chat with your AI Task Assistant")
    
    # Display current tasks in sidebar
    with st.sidebar:
        st.header("📋 Current Tasks")
        if st.button("🔄 Refresh Tasks"):
            pass  # Will refresh on rerun
        
        # Show tasks
        tasks = st.session_state.agent.db.get_all_tasks()
        if tasks:
            for task in tasks[:10]:  # Show latest 10
                status = "✅" if task['status'] == 'completed' else "⏳"
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "🟡")
                st.write(f"{status} {priority_color} **[{task['id']}]** {task['description']}")
        else:
            st.write("No tasks yet!")
    
    # Main chat interface
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "What would you like me to help you with?",
            placeholder="e.g., 'Add a high priority task to finish the project by Friday'",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("Send", type="primary")
    
    # Process input
    if send_button and user_input:
        with st.spinner("🤔 Processing your request..."):
            response = st.session_state.agent.process_input(user_input)
        
        # Display response
        st.success(response)
        
        # Clear input
        st.rerun()
    
    # Example commands
    st.subheader("💡 Example Commands")
    examples = [
        "Add a high priority task to call the client tomorrow",
        "Remind me to buy groceries",
        "Show me all my tasks",
        "Mark task 1 as completed",
        "Delete task 2"
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"Try: {example}", key=f"example_{i}"):
            with st.spinner("Processing..."):
                response = st.session_state.agent.process_input(example)
            st.success(response)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using OpenAI, SQLite, and Streamlit")

if __name__ == "__main__":
    main()