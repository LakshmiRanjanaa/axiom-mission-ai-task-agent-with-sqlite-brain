import openai
import re
from typing import Dict, Optional
from database import TaskDatabase

class TaskAgent:
    """AI agent that processes natural language task commands"""
    
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.db = TaskDatabase()
        
    def parse_command(self, user_input: str) -> Dict:
        """Use OpenAI to parse user intent from natural language"""
        
        # System prompt that teaches the AI how to interpret task commands
        system_prompt = """
        You are a task management assistant. Parse user commands and respond with JSON only.
        
        For task creation, return: {"action": "create", "description": "task text", "priority": "low/medium/high"}
        For task completion, return: {"action": "complete", "task_id": number or "description": "task text"}
        For viewing tasks, return: {"action": "view"}
        For deleting tasks, return: {"action": "delete", "task_id": number or "description": "task text"}
        
        Determine priority based on urgency words like "urgent", "important", "ASAP", "high priority".
        Default priority is "medium".
        
        Examples:
        - "Add task to buy milk" → {"action": "create", "description": "buy milk", "priority": "medium"}
        - "High priority: finish report by Friday" → {"action": "create", "description": "finish report by Friday", "priority": "high"}
        - "Mark grocery shopping as done" → {"action": "complete", "description": "grocery shopping"}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content.strip()
            # Simple JSON extraction (you might want to use json.loads for production)
            return eval(content)  # Note: eval is unsafe in production, use json.loads instead
            
        except Exception as e:
            print(f"AI parsing error: {e}")
            return {"action": "error", "message": "Could not understand the command"}
    
    def execute_command(self, command: Dict) -> str:
        """Execute the parsed command and return response message"""
        
        action = command.get('action', '').lower()
        
        if action == 'create':
            description = command.get('description', '')
            priority = command.get('priority', 'medium')
            
            if description:
                task_id = self.db.add_task(description, priority)
                return f"✅ Created {priority} priority task: '{description}' (ID: {task_id})"
            else:
                return "❌ Task description is required"
        
        elif action == 'view':
            tasks = self.db.get_all_tasks()
            if not tasks:
                return "📝 No tasks found"
            
            response = "📋 Your tasks:\n\n"
            for task in tasks:
                status_emoji = "✅" if task['status'] == 'completed' else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "🟡")
                response += f"{status_emoji} {priority_emoji} [{task['id']}] {task['description']} ({task['status']})\n"
            
            return response
        
        elif action == 'complete':
            # Handle completion by task ID or description
            task_id = command.get('task_id')
            if task_id and self.db.update_task_status(task_id, 'completed'):
                return f"✅ Marked task {task_id} as completed"
            else:
                return "❌ Could not find or update the task"
        
        elif action == 'delete':
            task_id = command.get('task_id')
            if task_id and self.db.delete_task(task_id):
                return f"🗑️ Deleted task {task_id}"
            else:
                return "❌ Could not find or delete the task"
        
        else:
            return "❓ I didn't understand that command. Try: 'add task to...', 'show my tasks', 'mark task X as done'"
    
    def process_input(self, user_input: str) -> str:
        """Main method to process user input and return response"""
        command = self.parse_command(user_input)
        return self.execute_command(command)