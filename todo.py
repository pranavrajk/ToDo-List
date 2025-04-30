import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        self.root.geometry("900x650")
        
        # Initialize tasks and undo stack
        self.tasks = {}
        self.undo_stack = []
        self.load_tasks()
        
        # Configure style
        self.configure_styles()
        
        # Create GUI elements
        self.create_widgets()
        self.update_task_list()
    
    def configure_styles(self):
        """Configure modern styling for the application"""
        style = ttk.Style()
        
        # Theme settings
        style.theme_use('clam')
        
        # Colors
        self.bg_color = "#f5f5f5"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.accent_color = "#4fc3f7"
        self.complete_color = "#81c784"
        self.error_color = "#ff8a80"
        
        # Configure styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, font=('Helvetica', 10))
        style.configure("TButton", font=('Helvetica', 10), padding=5)
        style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.map("TButton", 
                background=[('active', self.secondary_color)],
                foreground=[('active', 'white')])
        
        # Custom styles
        style.configure("Primary.TButton", background=self.primary_color, foreground="white")
        style.configure("Accent.TButton", background=self.accent_color, foreground="white")
        style.configure("Error.TButton", background=self.error_color, foreground="white")
        
        self.root.configure(background=self.bg_color)
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (task entry)
        left_frame = ttk.Frame(main_frame, style="TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        header = ttk.Frame(left_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="To-Do List", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Task description
        ttk.Label(left_frame, text="Task Description:").pack(anchor=tk.W)
        self.task_entry = ttk.Entry(left_frame, width=40, font=('Helvetica', 10))
        self.task_entry.pack(fill=tk.X, pady=5)
        
        # Due date
        ttk.Label(left_frame, text="Due Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.date_entry = ttk.Entry(left_frame, width=40, font=('Helvetica', 10))
        self.date_entry.pack(fill=tk.X, pady=5)
        self.date_entry.insert(0, date.today().isoformat())
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Add Task", style="Primary.TButton", 
                  command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", style="Error.TButton", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mark Complete", style="Accent.TButton", 
                  command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Undo Last Action", 
                  command=self.undo_last_action).pack(side=tk.LEFT, padx=5)
        
        # Right panel (task display)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Date filter
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Filter by Date:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_var.set("all")  # Default to showing all tasks
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, 
                       value="all", command=self.update_task_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Today", variable=self.filter_var, 
                       value="today", command=self.update_task_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Specific Date", variable=self.filter_var, 
                       value="specific", command=self.update_task_list).pack(side=tk.LEFT, padx=5)
        
        self.specific_date_entry = ttk.Entry(filter_frame, width=12)
        self.specific_date_entry.pack(side=tk.LEFT, padx=5)
        self.specific_date_entry.insert(0, date.today().isoformat())
        self.specific_date_entry.config(state=tk.DISABLED)
        
        # Task list
        self.task_tree = ttk.Treeview(right_frame, columns=("Status", "Description", "Due Date"), 
                                     show="headings", selectmode="browse")
        
        # Configure columns
        self.task_tree.column("Status", width=50, anchor=tk.CENTER)
        self.task_tree.column("Description", width=300, anchor=tk.W)
        self.task_tree.column("Due Date", width=100, anchor=tk.CENTER)
        
        # Set headings
        self.task_tree.heading("Status", text="✓")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Due Date", text="Due Date")
        
        self.task_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tag configurations for completed tasks
        self.task_tree.tag_configure("completed", foreground="#666666", background="#e8f5e9")
        
        # Bind double-click to mark complete
        self.task_tree.bind("<Double-1>", lambda e: self.mark_complete())
    
    def push_to_undo_stack(self, action_type, task_data):
        """Push an action to the undo stack"""
        self.undo_stack.append({
            "type": action_type,
            "data": task_data
        })
    
    def undo_last_action(self):
        """Undo the last action performed"""
        if not self.undo_stack:
            messagebox.showinfo("Info", "Nothing to undo!")
            return
        
        last_action = self.undo_stack.pop()
        
        if last_action["type"] == "add":
            # Undo add action by deleting the task
            due_date = last_action["data"]["due_date"]
            description = last_action["data"]["description"]
            
            for i, task in enumerate(self.tasks[due_date]):
                if task["description"] == description:
                    del self.tasks[due_date][i]
                    break
            
            # Remove date if no tasks left
            if len(self.tasks[due_date]) == 0:
                del self.tasks[due_date]
            
            messagebox.showinfo("Undo", "Added task removed")
        
        elif last_action["type"] == "delete":
            # Undo delete action by restoring the task
            due_date = last_action["data"]["due_date"]
            task = last_action["data"]["task"]
            
            if due_date not in self.tasks:
                self.tasks[due_date] = []
            
            self.tasks[due_date].append(task)
            messagebox.showinfo("Undo", "Deleted task restored")
        
        elif last_action["type"] == "complete":
            # Undo complete action by marking incomplete
            due_date = last_action["data"]["due_date"]
            description = last_action["data"]["description"]
            
            for task in self.tasks[due_date]:
                if task["description"] == description:
                    task["completed"] = False
                    break
            
            messagebox.showinfo("Undo", "Completion status reverted")
        
        self.save_tasks()
        self.update_task_list()
    
    def add_task(self):
        """Add a new task to the list"""
        description = self.task_entry.get().strip()
        due_date = self.date_entry.get().strip()
        
        if not description:
            messagebox.showerror("Error", "Task description cannot be empty!")
            return
        
        try:
            # Validate the date format
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
        
        task = {
            "description": description,
            "completed": False,
            "created": datetime.now().isoformat()
        }
        
        # Add to undo stack
        self.push_to_undo_stack("add", {
            "due_date": due_date,
            "description": description
        })
        
        if due_date not in self.tasks:
            self.tasks[due_date] = []
        
        self.tasks[due_date].append(task)
        self.save_tasks()
        self.update_task_list()
        
        # Clear the entry fields
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())
    
    def delete_task(self):
        """Delete the selected task"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No task selected!")
            return
        
        # Get the task details from the selected row
        item = self.task_tree.item(selected_item)
        due_date = item['values'][2]
        description = item['values'][1]
        
        # Find the task
        task_to_delete = None
        for i, task in enumerate(self.tasks[due_date]):
            if task['description'] == description:
                task_to_delete = task
                break
        
        if task_to_delete:
            # Add to undo stack before deleting
            self.push_to_undo_stack("delete", {
                "due_date": due_date,
                "task": task_to_delete
            })
            
            # Remove the task
            del self.tasks[due_date][i]
            
            # Remove the date if no tasks left
            if len(self.tasks[due_date]) == 0:
                del self.tasks[due_date]
            
            self.save_tasks()
            self.update_task_list()
    
    def mark_complete(self):
        """Mark the selected task as complete"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No task selected!")
            return
        
        # Get the task details from the selected row
        item = self.task_tree.item(selected_item)
        due_date = item['values'][2]
        description = item['values'][1]
        
        # Find and update the task
        for task in self.tasks[due_date]:
            if task['description'] == description:
                # Add to undo stack before changing
                self.push_to_undo_stack("complete", {
                    "due_date": due_date,
                    "description": description
                })
                
                task['completed'] = True
                break
        
        self.save_tasks()
        self.update_task_list()
    
    def update_task_list(self):
        """Update the task list display based on current filter"""
        # Clear the current view
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Enable/disable specific date entry based on selection
        if self.filter_var.get() == "specific":
            self.specific_date_entry.config(state=tk.NORMAL)
            specific_date = self.specific_date_entry.get().strip()
        else:
            self.specific_date_entry.config(state=tk.DISABLED)
        
        # Add tasks to the view based on filter
        for due_date in sorted(self.tasks.keys()):
            # Apply filters
            if self.filter_var.get() == "today" and due_date != date.today().isoformat():
                continue
            if self.filter_var.get() == "specific" and due_date != specific_date:
                continue
            
            for task in self.tasks[due_date]:
                status = "✓" if task['completed'] else ""
                tags = ("completed",) if task['completed'] else ()
                self.task_tree.insert("", tk.END, values=(status, task['description'], due_date), tags=tags)
    
    def save_tasks(self):
        """Save tasks to a JSON file"""
        try:
            with open("todo_data.json", "w") as f:
                json.dump(self.tasks, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from a JSON file"""
        try:
            with open("todo_data.json", "r") as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
            self.tasks = {}

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()