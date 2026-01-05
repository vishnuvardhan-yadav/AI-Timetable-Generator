import tkinter as tk
from tkinter import messagebox, filedialog
import random
from deap import base, creator, tools

# Fixed days for scheduling
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class TimetableApp:
    def _init_(self, root):
        self.root = root
        self.root.title("AI-Based Timetable Generator with Scheduling and Deadlines")
        
        # Allow window to be resizable and adjust dynamically
        self.root.geometry("850x950")  # Set the initial size, but it will resize based on content
        self.root.grid_rowconfigure(0, weight=1)  # Allow content area to expand
        self.root.grid_columnconfigure(0, weight=1)  # Allow content area to expand
        
        self.create_widgets()

    def create_widgets(self):
        # Styling for Frames
        frame_style = {"padx": 20, "pady": 20, "relief": "groove", "bd": 2}
        
        # Section 1: Session Timings Input
        self.timings_frame = tk.LabelFrame(self.root, text="Enter Session Timings", padx=15, pady=15, relief="groove", bd=2)
        self.timings_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.session_timings = {}
        default_timings = {
            "Morning Session 1": "10:00-11:30",
            "Morning Session 2": "11:30-1:00",
            "Afternoon Session 1": "2:00-3:30",
            "Afternoon Session 2": "3:30-5:00"
        }

        for session, default_time in default_timings.items():
            frame = tk.Frame(self.timings_frame)
            frame.pack(pady=8, anchor="w")
            tk.Label(frame, text=f"{session}:", width=30, anchor="w").pack(side="left")
            entry = tk.Entry(frame, width=20)
            entry.insert(0, default_time)  # Set default time
            entry.pack(side="left", padx=5)
            self.session_timings[session] = entry

        # Section 2: Subjects Input
        self.subjects_frame = tk.LabelFrame(self.root, text="Subjects", padx=15, pady=15, relief="groove", bd=2)
        self.subjects_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        tk.Label(self.subjects_frame, text="Enter Subjects (comma separated):").pack(side="left", padx=10)
        self.subjects_entry = tk.Entry(self.subjects_frame, width=50)
        self.subjects_entry.pack(side="left", padx=10)
        self.subjects_btn = tk.Button(self.subjects_frame, text="Set Subjects", command=self.set_subjects, relief="raised", bg="#4CAF50", fg="white", font=("Arial", 12))
        self.subjects_btn.pack(side="left", padx=10)

        # Section 3: Deadlines for Subjects
        self.deadlines_frame = tk.LabelFrame(self.root, text="Set Deadlines for Subjects", padx=15, pady=15, relief="groove", bd=2)
        self.deadlines_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.subject_deadlines = {}
        self.deadline_entries = {}

        # Availability and Scheduling Logic
        self.availability_frame = None
        self.subjects = []
        self.availability_entries = {}

        self.generate_btn = None
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12), fg="blue", anchor="w", justify="left")
        self.result_label.grid(row=3, column=0, pady=20, padx=20, sticky="ew")

    def set_subjects(self):
        subjects_input = self.subjects_entry.get().strip()
        if not subjects_input:
            messagebox.showerror("Error", "Please enter at least one subject.")
            return

        self.subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]

        if not self.subjects:
            messagebox.showerror("Error", "Please enter valid subject names.")
            return

        if self.availability_frame:
            self.availability_frame.destroy()
        self.availability_entries.clear()

        # Availability Section
        self.availability_frame = tk.LabelFrame(self.root, text="Faculty Availability", padx=15, pady=15, relief="groove", bd=2)
        self.availability_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        tk.Label(self.availability_frame, text="Enter availability per subject (comma-separated time slots)").pack(pady=8)

        for subject in self.subjects:
            frame = tk.Frame(self.availability_frame)
            frame.pack(pady=8, anchor="w")
            tk.Label(frame, text=f"{subject}:", width=25, anchor="w").pack(side="left", padx=5)
            entry = tk.Entry(frame, width=60)
            entry.pack(side="left", padx=5)
            self.availability_entries[subject] = entry

        # Deadlines for Subjects
        self.deadlines_frame = tk.LabelFrame(self.root, text="Set Deadlines", padx=15, pady=15, relief="groove", bd=2)
        self.deadlines_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        for subject in self.subjects:
            frame = tk.Frame(self.deadlines_frame)
            frame.pack(pady=8, anchor="w")
            tk.Label(frame, text=f"Deadline for {subject}:", width=25, anchor="w").pack(side="left", padx=5)
            entry = tk.Entry(frame, width=20)
            entry.pack(side="left", padx=5)
            self.deadline_entries[subject] = entry

        if not self.generate_btn:
            self.generate_btn = tk.Button(self.root, text="Generate Timetable", command=self.generate_timetable, relief="raised", bg="#FF6347", fg="white", font=("Arial", 12))
            self.generate_btn.grid(row=6, column=0, pady=20, padx=20, sticky="ew")

    def create_time_slots(self):
        session_times = {}
        for session, entry in self.session_timings.items():
            timing = entry.get().strip()
            if not timing:
                messagebox.showerror("Error", f"Please enter timing for {session}.")
                return None
            session_times[session] = timing

        slots = []
        for day in days:
            for session in session_times:
                slot = f"{day} {session} ({session_times[session]})"
                slots.append(slot)
        return slots

    def generate_timetable(self):
        time_slots = self.create_time_slots()
        if time_slots is None:
            return

        faculty_availability = {}
        for subject, entry in self.availability_entries.items():
            slots = [slot.strip() for slot in entry.get().split(",") if slot.strip()]
            if not slots:
                messagebox.showerror("Error", f"Please enter at least one available session for {subject}.")
                return
            faculty_availability[subject] = slots

        deadlines = {}
        for subject, entry in self.deadline_entries.items():
            deadline = entry.get().strip()
            if deadline:
                deadlines[subject] = deadline
            else:
                deadlines[subject] = None

        best_timetable = self.run_genetic_algorithm(faculty_availability, time_slots, deadlines)

        if best_timetable:
            self.display_timetable(best_timetable)
        else:
            self.result_label.config(text="No valid timetable found.")

    def display_timetable(self, best_timetable):
        timetable_window = tk.Toplevel(self.root)
        timetable_window.title("Generated Timetable")
        timetable_window.geometry("700x500")
        timetable_window.configure(bg="lightblue")

        timetable_frame = tk.Frame(timetable_window)
        timetable_frame.pack(padx=20, pady=20)

        # Create the header row for days
        header_row = tk.Frame(timetable_frame)
        header_row.grid(row=0, column=0, padx=5, pady=5)
        for day in days:
            tk.Label(header_row, text=day, width=15, relief="groove", font=("Arial", 12)).grid(row=0, column=days.index(day), padx=5)

        # Create a list to hold the full timetable (session + subject)
        timetable_grid = {}

        # Populate the timetable with subjects and time slots
        for i, session in enumerate(self.session_timings):
            session_frame = tk.Frame(timetable_frame)
            session_frame.grid(row=i+1, column=0, padx=5, pady=5)
            tk.Label(session_frame, text=session, width=20, relief="groove", font=("Arial", 12)).grid(row=i+1, column=0)

            for j, day in enumerate(days):
                subject = best_timetable[i + j*len(self.session_timings)] if i + j*len(self.session_timings) < len(best_timetable) else ""
                subject_text = self.subjects[best_timetable.index(subject)] if subject else ""
                timetable_grid[(i, j)] = subject_text
                tk.Label(session_frame, text=subject_text, width=20, relief="groove", font=("Arial", 12)).grid(row=i+1, column=j+1)

        save_btn = tk.Button(timetable_window, text="Save Timetable", command=lambda: self.save_timetable(timetable_grid), relief="raised", bg="#32CD32", fg="white", font=("Arial", 12))
        save_btn.pack(pady=10)

    def save_timetable(self, timetable_grid):
        timetable_text = "\n".join([f"Session {i+1} on {days[j]}: {timetable_grid[(i, j)]}" for i in range(len(self.session_timings)) for j in range(len(days))])
        file = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            file.write(timetable_text)
            file.close()

    def run_genetic_algorithm(self, faculty_availability, time_slots, deadlines):
        def fitness(individual):
            score = 0
            for i, subject in enumerate(self.subjects):
                assigned_slot = individual[i]
                if assigned_slot in faculty_availability.get(subject, []):
                    score += 1  # Faculty availability constraint
                if deadlines[subject] and assigned_slot == deadlines[subject]:
                    score += 2  # Deadline fulfillment constraint
            return score,

        try:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        except:
            pass
        try:
            creator.create("Individual", list, fitness=creator.FitnessMax)
        except:
            pass

        toolbox = base.Toolbox()
        toolbox.register("attr_time", random.choice, time_slots)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_time, n=len(self.subjects))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", fitness)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        population = toolbox.population(n=100)
        for _ in range(200):
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.7:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values, child2.fitness.values
            for mutant in offspring:
                if random.random() < 0.2:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            population[:] = offspring
            for ind in population:
                if not ind.fitness.valid:
                    ind.fitness.values = toolbox.evaluate(ind)

        return max(population, key=lambda ind: ind.fitness.values[0], default=None)


if _name_ == "_main_":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()
