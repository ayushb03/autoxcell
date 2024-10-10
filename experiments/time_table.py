from ortools.sat.python import cp_model

class TimetableSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, teachers, classes, subjects, rooms, time_slots, timetable):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.teachers = teachers
        self.classes = classes
        self.subjects = subjects
        self.rooms = rooms
        self.time_slots = time_slots  # Assuming it's a 1D list of available time slots
        self.timetable = timetable

    def on_solution_callback(self):
        for class_id in range(len(self.classes)):
            for subject_id in range(len(self.subjects[class_id])):
                teacher = self.teachers[class_id][subject_id]
                room = self.rooms[class_id][subject_id]
                time_slot = self.Value(self.timetable[(class_id, subject_id)]['time_slot'])  # Accessing time slot from the timetable
                print(f"Class {self.classes[class_id]}: {self.subjects[class_id][subject_id]} -> "
                      f"Teacher {teacher}, Room {room}, Time Slot {time_slot}")

def timetable_generator(classes, teachers, subjects, time_slots, rooms):
    model = cp_model.CpModel()
    
    num_classes = len(classes)
    num_teachers = len(teachers)
    num_rooms = len(rooms)
    num_time_slots = len(time_slots)
    
    # Create decision variables
    timetable = {}
    for class_id in range(num_classes):
        for subject_id in range(len(subjects[class_id])):
            timetable[(class_id, subject_id)] = {
                'teacher': model.NewIntVar(0, num_teachers - 1, f'teacher_{class_id}_{subject_id}'),
                'room': model.NewIntVar(0, num_rooms - 1, f'room_{class_id}_{subject_id}'),
                'time_slot': model.NewIntVar(0, num_time_slots - 1, f'time_slot_{class_id}_{subject_id}')  # Decision variable for time slots
            }
    
    # Add Constraints
    for class_id in range(num_classes):
        for subject_id in range(len(subjects[class_id])):
            # Each subject must be assigned to a unique time slot for each class
            time_slot = timetable[(class_id, subject_id)]['time_slot']
            model.AddAllDifferent([timetable[(class_id, s_id)]['time_slot'] for s_id in range(len(subjects[class_id]))])
            
            # Teacher availability constraint: a teacher can't teach multiple classes at the same time
            for other_class_id in range(class_id + 1, num_classes):
                other_time_slot = timetable[(other_class_id, subject_id)]['time_slot']
                model.Add(time_slot != other_time_slot)
    
    # Add more constraints like room capacities, teacher preferences, etc.

    # Create solver
    solver = cp_model.CpSolver()
    
    # Set search strategy (Genetic Algorithm with Local Search & Simulated Annealing can be simulated by adjusting search params)
    solver.parameters.max_time_in_seconds = 5.0  # Time limit of 60 seconds
    
    solution_printer = TimetableSolutionPrinter(teachers, classes, subjects, rooms, time_slots, timetable)
    solver.SearchForAllSolutions(model, solution_printer)


# Sample data
classes = ['Class 1', 'Class 2', 'Class 3']
teachers = [['T1', 'T2'], ['T3', 'T4'], ['T5', 'T6']]
subjects = [['Math', 'English'], ['Science', 'History'], ['Art', 'Music']]
time_slots = list(range(5))  # Time slots from 0 to 4
rooms = ['Room 101', 'Room 102', 'Room 103']

# Call timetable generator
timetable_generator(classes, teachers, subjects, time_slots, rooms)
