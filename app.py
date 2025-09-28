import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Task, Goal, Event, Base
import json

class BusynessBusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Busyness Buster")
        self.root.geometry("800x600")
        
        # Initialize database connection
        self.setup_database()
        
        # API base URL (assuming FastAPI server is running)
        self.api_base_url = "http://localhost:8000"
        
        # Check if FastAPI server is running
        self.check_server_status()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tasks_tab()
        self.create_goals_tab()
        self.create_active_tab()
        self.create_sync_tab()
        
    def setup_database(self):
        """Initialize database connection"""
        try:
            # Direct database connection for GUI
            engine = create_engine("sqlite:///busyness.db")
            SessionLocal = sessionmaker(bind=engine)
            self.db_session = SessionLocal()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.db_session = None
            
    def check_server_status(self):
        """Check if the FastAPI server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/docs", timeout=2)
            if response.status_code == 200:
                print("FastAPI server is running")
            else:
                messagebox.showwarning("Server Warning", "FastAPI server may not be running properly. Some features may not work.")
        except requests.exceptions.RequestException:
            messagebox.showwarning("Server Warning", "FastAPI server is not running. Please start it with 'uvicorn main:app' to use sync and analysis features.")
        
    def create_tasks_tab(self):
        # Tasks tab
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Add Tasks")
        
        # Task input section
        input_frame = ttk.LabelFrame(tasks_frame, text="New Task", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Task title
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.task_title = ttk.Entry(input_frame, width=40)
        self.task_title.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Task description
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.task_desc = tk.Text(input_frame, height=3, width=40)
        self.task_desc.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Priority (1-10 slider)
        ttk.Label(input_frame, text="Priority:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.task_priority = ttk.Scale(input_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.task_priority.set(6)  # Default to 6 (medium)
        self.task_priority.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.task_priority_label = ttk.Label(input_frame, text="6")
        self.task_priority_label.grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Goal selection
        ttk.Label(input_frame, text="Goal:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.task_goal_id = ttk.Combobox(input_frame, state="readonly")
        self.task_goal_id.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        self.populate_goals_combobox()
        
        # Due date
        ttk.Label(input_frame, text="Due Date:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.task_due_date = ttk.Entry(input_frame, width=20)
        self.task_due_date.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        ttk.Label(input_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Add task button
        add_task_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_task_btn.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=10)
        
        # Configure priority slider callback
        self.task_priority.configure(command=self.update_task_priority_label)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
    def create_goals_tab(self):
        # Goals tab
        goals_frame = ttk.Frame(self.notebook)
        self.notebook.add(goals_frame, text="Add Goals")
        
        # Goal input section
        input_frame = ttk.LabelFrame(goals_frame, text="New Goal", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Goal title
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.goal_title = ttk.Entry(input_frame, width=40)
        self.goal_title.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Priority (1-10 slider)
        ttk.Label(input_frame, text="Priority:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.goal_priority = ttk.Scale(input_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.goal_priority.set(6)  # Default to 6 (medium)
        self.goal_priority.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.goal_priority_label = ttk.Label(input_frame, text="6")
        self.goal_priority_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Forecast
        ttk.Label(input_frame, text="Forecast:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.goal_forecast = ttk.Combobox(input_frame, values=["Short", "Medium", "Long"], state="readonly")
        self.goal_forecast.set("Medium")
        self.goal_forecast.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Add goal button
        add_goal_btn = ttk.Button(input_frame, text="Add Goal", command=self.add_goal)
        add_goal_btn.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=10)
        
        # Configure priority slider callback
        self.goal_priority.configure(command=self.update_goal_priority_label)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
    def create_active_tab(self):
        # Active items tab
        active_frame = ttk.Frame(self.notebook)
        self.notebook.add(active_frame, text="Active Items")
        
        # Create paned window for side-by-side view
        paned = ttk.PanedWindow(active_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Active tasks
        tasks_frame = ttk.LabelFrame(paned, text="Active Tasks", padding="5")
        paned.add(tasks_frame, weight=1)
        
        self.active_tasks_listbox = tk.Listbox(tasks_frame)
        self.active_tasks_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Active goals
        goals_frame = ttk.LabelFrame(paned, text="Active Goals", padding="5")
        paned.add(goals_frame, weight=1)
        
        self.active_goals_listbox = tk.Listbox(goals_frame)
        self.active_goals_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(active_frame, text="Refresh", command=self.refresh_active)
        refresh_btn.pack(pady=5)
        
        # Load active items
        self.refresh_active()
        
    def create_sync_tab(self):
        # Sync and analyze tab
        sync_frame = ttk.Frame(self.notebook)
        self.notebook.add(sync_frame, text="Sync & Analyze")
        
        # Sync section
        sync_section = ttk.LabelFrame(sync_frame, text="Live Event Sync", padding="10")
        sync_section.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(sync_section, text="Connect to Google Calendar for live event sync").pack(anchor=tk.W)
        sync_btn = ttk.Button(sync_section, text="Sync Events", command=self.sync_events)
        sync_btn.pack(pady=5)
        
        # Analysis section
        analysis_section = ttk.LabelFrame(sync_frame, text="Analysis", padding="10")
        analysis_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(analysis_section, text="Analyze your productivity patterns").pack(anchor=tk.W)
        analyze_btn = ttk.Button(analysis_section, text="Analyze", command=self.analyze_data)
        analyze_btn.pack(pady=5)
        
        # Analysis results
        self.analysis_text = tk.Text(analysis_section, height=15, width=70)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def update_task_priority_label(self, value):
        self.task_priority_label.config(text=f"{int(float(value))}")
        
    def update_goal_priority_label(self, value):
        self.goal_priority_label.config(text=f"{int(float(value))}")
        
    def populate_goals_combobox(self):
        """Populate the goals combobox with active goals"""
        if not self.db_session:
            return
            
        try:
            active_goals = self.db_session.query(Goal).filter(Goal.accomplished == False).all()
            goal_options = ["None"] + [f"{goal.goal} (ID: {goal.id})" for goal in active_goals]
            self.task_goal_id['values'] = goal_options
            self.task_goal_id.set("None")
        except Exception as e:
            print(f"Error populating goals: {e}")
        
    def add_task(self):
        title = self.task_title.get().strip()
        priority = int(self.task_priority.get())
        due_date_text = self.task_due_date.get().strip()
        goal_selection = self.task_goal_id.get()
        
        if not title:
            messagebox.showerror("Error", "Please enter a task title")
            return
        
        # Parse goal_id
        goal_id = None
        if goal_selection and goal_selection != "None":
            try:
                goal_id = int(goal_selection.split("ID: ")[1].rstrip(")"))
            except (IndexError, ValueError):
                messagebox.showerror("Error", "Invalid goal selection")
                return
        
        # Parse due date
        due_date = None
        if due_date_text:
            try:
                due_date = datetime.strptime(due_date_text, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        
        try:
            # Create task in database
            task = Task(
                title=title,
                priority=priority,
                due_date=due_date,
                completed=False,
                goal_id=goal_id
            )
            
            self.db_session.add(task)
            self.db_session.commit()
            
            self.clear_task_form()
            messagebox.showinfo("Success", "Task added successfully!")
            self.refresh_active()
            self.populate_goals_combobox()  # Refresh goals list
            
        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")
        
    def add_goal(self):
        title = self.goal_title.get().strip()
        priority = int(self.goal_priority.get())
        forecast = self.goal_forecast.get()
        
        if not title:
            messagebox.showerror("Error", "Please enter a goal title")
            return
        
        try:
            # Create goal in database
            goal = Goal(
                goal=title,  # Using 'goal' field as per database schema
                priority=priority,
                accomplished=False,
                forecast=forecast
            )
            
            self.db_session.add(goal)
            self.db_session.commit()
            
            self.clear_goal_form()
            messagebox.showinfo("Success", "Goal added successfully!")
            self.refresh_active()
            self.populate_goals_combobox()  # Refresh goals list
            
        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Error", f"Failed to add goal: {str(e)}")
        
    def clear_task_form(self):
        self.task_title.delete(0, tk.END)
        self.task_desc.delete("1.0", tk.END)
        self.task_priority.set(6)
        self.task_due_date.delete(0, tk.END)
        self.task_goal_id.set("None")
        
    def clear_goal_form(self):
        self.goal_title.delete(0, tk.END)
        self.goal_priority.set(6)
        self.goal_forecast.set("Medium")
        
    def refresh_active(self):
        if not self.db_session:
            return
            
        # Clear existing items
        self.active_tasks_listbox.delete(0, tk.END)
        self.active_goals_listbox.delete(0, tk.END)
        
        try:
            # Query active tasks from database
            active_tasks = self.db_session.query(Task).filter(Task.completed == False).all()
            for task in active_tasks:
                display_text = f"{task.title} (Priority: {task.priority})"
                if task.due_date:
                    display_text += f" - Due: {task.due_date.strftime('%Y-%m-%d')}"
                if task.goal_id:
                    # Get goal title for display
                    goal = self.db_session.query(Goal).filter(Goal.id == task.goal_id).first()
                    if goal:
                        display_text += f" - Goal: {goal.goal}"
                self.active_tasks_listbox.insert(tk.END, display_text)
            
            # Query active goals from database
            active_goals = self.db_session.query(Goal).filter(Goal.accomplished == False).all()
            for goal in active_goals:
                display_text = f"{goal.goal} (Priority: {goal.priority})"
                if goal.forecast:
                    display_text += f" - {goal.forecast} term"
                self.active_goals_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to refresh data: {str(e)}")
                
    def sync_events(self):
        """Sync events from Google Calendar using the FastAPI backend"""
        def sync_thread():
            try:
                # Make API call to sync events
                response = requests.post(f"{self.api_base_url}/events/sync")
                if response.status_code == 200:
                    events = response.json()
                    self.root.after(0, lambda: messagebox.showinfo("Sync Complete", f"Synced {len(events)} events from Google Calendar!"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Sync Error", f"Failed to sync events: {response.text}"))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Could not connect to the FastAPI server. Make sure it's running on localhost:8000"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Sync Error", f"Unexpected error: {str(e)}"))
        
        # Run sync in background thread to avoid blocking UI
        thread = threading.Thread(target=sync_thread)
        thread.daemon = True
        thread.start()
        
        messagebox.showinfo("Syncing", "Syncing events from Google Calendar...")
        
    def analyze_data(self):
        """Get AI analysis from the FastAPI backend"""
        def analyze_thread():
            try:
                # Make API call to get AI analysis
                response = requests.get(f"{self.api_base_url}/analysis/")
                if response.status_code == 200:
                    result = response.json()
                    analysis = result.get("analysis", "No analysis available")
                    self.root.after(0, lambda: self.display_analysis(analysis))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Analysis Error", f"Failed to get analysis: {response.text}"))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Could not connect to the FastAPI server. Make sure it's running on localhost:8000"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Analysis Error", f"Unexpected error: {str(e)}"))
        
        # Run analysis in background thread
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()
        
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", "Analyzing your productivity patterns...\nPlease wait...")
        
    def display_analysis(self, analysis):
        """Display the analysis results in the text widget"""
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", analysis)
        

def main():
    root = tk.Tk()
    app = BusynessBusterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
