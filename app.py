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
        
        # Add context menu for tasks
        self.tasks_context_menu = tk.Menu(self.root, tearoff=0)
        self.tasks_context_menu.add_command(label="Edit Task", command=self.edit_selected_task)
        self.tasks_context_menu.add_command(label="Delete Task", command=self.delete_selected_task)
        self.active_tasks_listbox.bind("<Button-3>", self.show_tasks_context_menu)
        
        # Active goals
        goals_frame = ttk.LabelFrame(paned, text="Active Goals", padding="5")
        paned.add(goals_frame, weight=1)
        
        self.active_goals_listbox = tk.Listbox(goals_frame)
        self.active_goals_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add context menu for goals
        self.goals_context_menu = tk.Menu(self.root, tearoff=0)
        self.goals_context_menu.add_command(label="Edit Goal", command=self.edit_selected_goal)
        self.goals_context_menu.add_command(label="Delete Goal", command=self.delete_selected_goal)
        self.active_goals_listbox.bind("<Button-3>", self.show_goals_context_menu)
        
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
    
    def show_tasks_context_menu(self, event):
        """Show context menu for tasks"""
        try:
            self.tasks_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tasks_context_menu.grab_release()
    
    def show_goals_context_menu(self, event):
        """Show context menu for goals"""
        try:
            self.goals_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.goals_context_menu.grab_release()
    
    def edit_selected_task(self):
        """Edit the selected task"""
        selection = self.active_tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return
        
        # Get task ID from the display text
        task_text = self.active_tasks_listbox.get(selection[0])
        task_id = self.extract_task_id_from_display(task_text)
        
        if task_id:
            self.open_task_edit_dialog(task_id)
        else:
            messagebox.showerror("Error", "Could not identify task ID")
    
    def delete_selected_task(self):
        """Delete the selected task"""
        selection = self.active_tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to delete")
            return
        
        # Get task ID from the display text
        task_text = self.active_tasks_listbox.get(selection[0])
        task_id = self.extract_task_id_from_display(task_text)
        
        if task_id:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
                self.delete_task_by_id(task_id)
        else:
            messagebox.showerror("Error", "Could not identify task ID")
    
    def edit_selected_goal(self):
        """Edit the selected goal"""
        selection = self.active_goals_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a goal to edit")
            return
        
        # Get goal ID from the display text
        goal_text = self.active_goals_listbox.get(selection[0])
        goal_id = self.extract_goal_id_from_display(goal_text)
        
        if goal_id:
            self.open_goal_edit_dialog(goal_id)
        else:
            messagebox.showerror("Error", "Could not identify goal ID")
    
    def delete_selected_goal(self):
        """Delete the selected goal"""
        selection = self.active_goals_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a goal to delete")
            return
        
        # Get goal ID from the display text
        goal_text = self.active_goals_listbox.get(selection[0])
        goal_id = self.extract_goal_id_from_display(goal_text)
        
        if goal_id:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this goal?"):
                self.delete_goal_by_id(goal_id)
        else:
            messagebox.showerror("Error", "Could not identify goal ID")
    
    def extract_task_id_from_display(self, task_text):
        """Extract task ID from display text"""
        try:
            # Look for pattern like "Task Title (Priority: X) - Due: YYYY-MM-DD - Goal: Z"
            # We need to get the task from database to find the ID
            if not self.db_session:
                return None
            
            # Extract task title (everything before " (Priority:")
            title_part = task_text.split(" (Priority:")[0]
            
            # Find the task in database
            task = self.db_session.query(Task).filter(Task.title == title_part, Task.completed == False).first()
            return task.id if task else None
        except Exception as e:
            print(f"Error extracting task ID: {e}")
            return None
    
    def extract_goal_id_from_display(self, goal_text):
        """Extract goal ID from display text"""
        try:
            # Look for pattern like "Goal Title (Priority: X) - Y term"
            if not self.db_session:
                return None
            
            # Extract goal title (everything before " (Priority:")
            title_part = goal_text.split(" (Priority:")[0]
            
            # Find the goal in database
            goal = self.db_session.query(Goal).filter(Goal.goal == title_part, Goal.accomplished == False).first()
            return goal.id if goal else None
        except Exception as e:
            print(f"Error extracting goal ID: {e}")
            return None
    
    def open_task_edit_dialog(self, task_id):
        """Open edit dialog for a task"""
        if not self.db_session:
            messagebox.showerror("Error", "Database connection not available")
            return
        
        # Get task from database
        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            messagebox.showerror("Error", "Task not found")
            return
        
        # Create edit dialog
        dialog = TaskEditDialog(self.root, task, self)
        self.root.wait_window(dialog.dialog)
    
    def open_goal_edit_dialog(self, goal_id):
        """Open edit dialog for a goal"""
        if not self.db_session:
            messagebox.showerror("Error", "Database connection not available")
            return
        
        # Get goal from database
        goal = self.db_session.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            messagebox.showerror("Error", "Goal not found")
            return
        
        # Create edit dialog
        dialog = GoalEditDialog(self.root, goal, self)
        self.root.wait_window(dialog.dialog)
    
    def delete_task_by_id(self, task_id):
        """Delete task by ID using API"""
        try:
            response = requests.delete(f"{self.api_base_url}/tasks/{task_id}")
            if response.status_code == 204:
                messagebox.showinfo("Success", "Task deleted successfully!")
                self.refresh_active()
                self.populate_goals_combobox()  # Refresh goals list
            else:
                messagebox.showerror("Error", f"Failed to delete task: {response.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the FastAPI server")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete task: {str(e)}")
    
    def delete_goal_by_id(self, goal_id):
        """Delete goal by ID using API"""
        try:
            response = requests.delete(f"{self.api_base_url}/goals/{goal_id}")
            if response.status_code == 204:
                messagebox.showinfo("Success", "Goal deleted successfully!")
                self.refresh_active()
                self.populate_goals_combobox()  # Refresh goals list
            else:
                messagebox.showerror("Error", f"Failed to delete goal: {response.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the FastAPI server")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete goal: {str(e)}")
    
    def update_task_via_api(self, task_id, task_data):
        """Update task via API"""
        try:
            response = requests.patch(f"{self.api_base_url}/tasks/{task_id}", json=task_data)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Task updated successfully!")
                self.refresh_active()
                self.populate_goals_combobox()  # Refresh goals list
                return True
            else:
                messagebox.showerror("Error", f"Failed to update task: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the FastAPI server")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task: {str(e)}")
            return False
    
    def update_goal_via_api(self, goal_id, goal_data):
        """Update goal via API"""
        try:
            response = requests.patch(f"{self.api_base_url}/goals/{goal_id}", json=goal_data)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Goal updated successfully!")
                self.refresh_active()
                self.populate_goals_combobox()  # Refresh goals list
                return True
            else:
                messagebox.showerror("Error", f"Failed to update goal: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the FastAPI server")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update goal: {str(e)}")
            return False


class TaskEditDialog:
    def __init__(self, parent, task, app):
        self.app = app
        self.task = task
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Task")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        self.create_form()
        
    def create_form(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar(value=self.task.title)
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.priority_var = tk.IntVar(value=self.task.priority)
        priority_scale = ttk.Scale(main_frame, from_=1, to=10, orient=tk.HORIZONTAL, 
                                 variable=self.priority_var, command=self.update_priority_label)
        priority_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.priority_label = ttk.Label(main_frame, text=str(self.task.priority))
        self.priority_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Due date
        ttk.Label(main_frame, text="Due Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        due_date_str = self.task.due_date.strftime("%Y-%m-%d") if self.task.due_date else ""
        self.due_date_var = tk.StringVar(value=due_date_str)
        due_date_entry = ttk.Entry(main_frame, textvariable=self.due_date_var, width=20)
        due_date_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        ttk.Label(main_frame, text="(YYYY-MM-DD)").grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Completed checkbox
        self.completed_var = tk.BooleanVar(value=self.task.completed)
        completed_check = ttk.Checkbutton(main_frame, text="Completed", variable=self.completed_var)
        completed_check.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Goal selection
        ttk.Label(main_frame, text="Goal:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.goal_var = tk.StringVar()
        goal_combo = ttk.Combobox(main_frame, textvariable=self.goal_var, state="readonly", width=37)
        goal_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Populate goals
        goal_options = ["None"]
        if self.app.db_session:
            try:
                active_goals = self.app.db_session.query(Goal).filter(Goal.accomplished == False).all()
                goal_options += [f"{goal.goal} (ID: {goal.id})" for goal in active_goals]
            except Exception as e:
                print(f"Error loading goals: {e}")
        
        goal_combo['values'] = goal_options
        
        # Set current goal if exists
        if self.task.goal_id:
            current_goal = None
            if self.app.db_session:
                current_goal = self.app.db_session.query(Goal).filter(Goal.id == self.task.goal_id).first()
            if current_goal:
                goal_combo.set(f"{current_goal.goal} (ID: {current_goal.id})")
            else:
                goal_combo.set("None")
        else:
            goal_combo.set("None")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def update_priority_label(self, value):
        self.priority_label.config(text=f"{int(float(value))}")
    
    def save_task(self):
        title = self.title_var.get().strip()
        priority = int(self.priority_var.get())
        due_date_text = self.due_date_var.get().strip()
        completed = self.completed_var.get()
        goal_selection = self.goal_var.get()
        
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
        
        # Prepare update data
        update_data = {
            "title": title,
            "priority": priority,
            "completed": completed,
            "goal_id": goal_id
        }
        
        if due_date:
            update_data["due_date"] = due_date.isoformat()
        
        # Update via API
        if self.app.update_task_via_api(self.task.id, update_data):
            self.dialog.destroy()


class GoalEditDialog:
    def __init__(self, parent, goal, app):
        self.app = app
        self.goal = goal
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Goal")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        self.create_form()
        
    def create_form(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar(value=self.goal.goal)
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.priority_var = tk.IntVar(value=self.goal.priority)
        priority_scale = ttk.Scale(main_frame, from_=1, to=10, orient=tk.HORIZONTAL, 
                                 variable=self.priority_var, command=self.update_priority_label)
        priority_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.priority_label = ttk.Label(main_frame, text=str(self.goal.priority))
        self.priority_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Forecast
        ttk.Label(main_frame, text="Forecast:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.forecast_var = tk.StringVar(value=self.goal.forecast or "Medium")
        forecast_combo = ttk.Combobox(main_frame, textvariable=self.forecast_var, 
                                    values=["Short", "Medium", "Long"], state="readonly", width=37)
        forecast_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Accomplished checkbox
        self.accomplished_var = tk.BooleanVar(value=self.goal.accomplished)
        accomplished_check = ttk.Checkbutton(main_frame, text="Accomplished", variable=self.accomplished_var)
        accomplished_check.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_goal).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def update_priority_label(self, value):
        self.priority_label.config(text=f"{int(float(value))}")
    
    def save_goal(self):
        title = self.title_var.get().strip()
        priority = int(self.priority_var.get())
        forecast = self.forecast_var.get()
        accomplished = self.accomplished_var.get()
        
        if not title:
            messagebox.showerror("Error", "Please enter a goal title")
            return
        
        # Prepare update data
        update_data = {
            "goal": title,
            "priority": priority,
            "forecast": forecast,
            "accomplished": accomplished
        }
        
        # Update via API
        if self.app.update_goal_via_api(self.goal.id, update_data):
            self.dialog.destroy()


def main():
    root = tk.Tk()
    app = BusynessBusterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
