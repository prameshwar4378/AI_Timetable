from collections import defaultdict
from .models import Teacher, ClassRoom, Subject, TeacherSubjectClassAssignment, DailyLectureTiming


from collections import defaultdict

def auto_adjust_teacher_lectures(teacher_subject_class_assignment, teacher_max_lectures):
    """
    Mutates teacher_subject_class_assignment so no teacher is assigned more lectures than allowed.
    Reduces lectures proportionally if overbooked.
    Returns a dict of assignments that were reduced: { (teacher_id, subject_id, class_id): (old, new) }
    """
    from math import floor

    # Group assignments by teacher
    teacher_to_assignments = {}
    for key, lectures in teacher_subject_class_assignment.items():
        teacher_id = key[0]
        teacher_to_assignments.setdefault(teacher_id, []).append((key, lectures))

    reduced = {}
    for teacher_id, assignments in teacher_to_assignments.items():
        max_allowed = teacher_max_lectures[teacher_id]
        total_assigned = sum(lectures for _, lectures in assignments)
        if total_assigned <= max_allowed:
            continue  # OK

        # Reduce proportionally
        print(f"⚠️ Teacher {teacher_id} overbooked ({total_assigned}/{max_allowed}). Reducing lecture counts...")
        ratio = max_allowed / total_assigned
        new_assignments = []
        for (key, lectures) in assignments:
            new_lectures = floor(lectures * ratio)
            # Ensure at least 1 if possible
            if new_lectures < 1 and max_allowed > 0:
                new_lectures = 1
            reduced[key] = (lectures, new_lectures)
            teacher_subject_class_assignment[key] = new_lectures
            new_assignments.append((key, new_lectures))
        # Fix any rounding errors by distributing remaining slots
        slots_used = sum(l for _, l in new_assignments)
        remaining = max_allowed - slots_used
        i = 0
        while remaining > 0 and i < len(new_assignments):
            key, new_lectures = new_assignments[i]
            teacher_subject_class_assignment[key] += 1
            reduced[key] = (reduced[key][0], teacher_subject_class_assignment[key])
            remaining -= 1
            i += 1

    return reduced


def preanalyze_assignments(teacher_subject_class_assignment, lecture_slots):
    print("🔎 Pre-analyzing assignments for conflicts...")

    class_to_slots = defaultdict(list)
    all_days = list(lecture_slots.keys())
    for day in all_days:
        for slot_idx in lecture_slots[day]:
            for class_id in set(cid for (_, _, cid) in teacher_subject_class_assignment):
                class_to_slots[class_id].append( (day, slot_idx) )

    slot_teacher_class = defaultdict(lambda: defaultdict(set))
    teacher_busy_in_slot = defaultdict(set)
    class_busy_in_slot = defaultdict(set)

    conflict_found = False  # <--- ADD THIS

    for (teacher_id, subject_id, class_id), lectures in sorted(teacher_subject_class_assignment.items()):
        available = [slot for slot in class_to_slots[class_id]
                     if slot not in teacher_busy_in_slot[teacher_id]
                     and slot not in class_busy_in_slot[class_id]]
        if len(available) < lectures:
            print(f"❌ CONFLICT: Not enough available slots for Teacher {teacher_id}, Subject {subject_id}, Class {class_id}: required {lectures}, available {len(available)}.")
            conflict_found = True
            continue
        chosen = available[:lectures]
        for slot in chosen:
            slot_teacher_class[slot][teacher_id].add(class_id)
            teacher_busy_in_slot[teacher_id].add(slot)
            class_busy_in_slot[class_id].add(slot)
        print(f"✅ Assignment OK: Teacher {teacher_id}, Subject {subject_id}, Class {class_id}: scheduled {lectures}.")

    for slot, t2c in slot_teacher_class.items():
        for teacher_id, class_ids in t2c.items():
            if len(class_ids) > 1:
                print(f"❌ DOUBLE-BOOKING: Teacher {teacher_id} in multiple classes {list(class_ids)} at slot {slot}.")
                conflict_found = True

    print("🔎 Pre-analysis complete.")
    return not conflict_found  # Return True if no conflict, False if any found





def extract_timetable_data():
    print("⏳ Extracting Teachers, Classes, Subjects...")
    teachers = list(Teacher.objects.values_list('id', flat=True))
    classes = list(ClassRoom.objects.values_list('id', flat=True))
    subjects = list(Subject.objects.values_list('id', flat=True))
    print(f"✔️ Teachers: {teachers}")
    print(f"✔️ Classes: {classes}")
    print(f"✔️ Subjects: {subjects}")

    print("⏳ Mapping Class Teachers...")
    class_teacher_map = {}
    for classroom in ClassRoom.objects.select_related('class_teacher'):
        if classroom.class_teacher:
            class_teacher_map[classroom.id] = classroom.class_teacher.id
    print(f"✔️ Class Teacher Map: {class_teacher_map}")

    print("⏳ Collecting Teacher-Subject-Class Assignments...")
    teacher_subject_class_assignment = {}
    subject_lecture_weekly_count = defaultdict(int)
    for assign in TeacherSubjectClassAssignment.objects.all():
        key = (assign.teacher.id, assign.subject.id, assign.classroom.id)
        teacher_subject_class_assignment[key] = assign.lectures_per_week
        subject_lecture_weekly_count[(assign.classroom.id, assign.subject.id)] += assign.lectures_per_week
    print(f"✔️ Teacher-Subject-Class Assignments: {teacher_subject_class_assignment}")
    print(f"✔️ Subject Lecture Weekly Count: {dict(subject_lecture_weekly_count)}")

    print("⏳ Computing Lecture Slots per Day...")
    lecture_slots = defaultdict(list)
    slot_idx_map = {}
    for timing in DailyLectureTiming.objects.select_related('time_slot'):
        day = timing.time_slot.day
        slot = timing.time_slot.lecture_number
        slot_idx_map[(day, slot)] = timing.id
        lecture_slots[day].append(timing.id)
    print(f"✔️ Lecture Slots per Day: {{day: count}} = {[ (k, len(v)) for k, v in lecture_slots.items() ]}")

    print("⏳ Setting Teacher Max Lectures...")
    MAX_LECTURES = 30
    teacher_max_lectures = {t.id: MAX_LECTURES for t in Teacher.objects.all()}
    print(f"✔️ Teacher Max Lectures: {teacher_max_lectures}")

    print("⏳ Marking All Teachers as Available (for demo)...")
    teacher_availability = defaultdict(lambda: True)

    print("⏳ Collecting Saturday Lecture Slots...")
    saturday_lecture_slots = [
        timing.id
        for timing in DailyLectureTiming.objects.select_related('time_slot').filter(time_slot__day='Saturday')
    ]
    print(f"✔️ Saturday Lecture Slots: {saturday_lecture_slots}")

    print("✅ Data Extraction Complete.")

    # Auto adjust teacher lectures if overbooked
    reduced = auto_adjust_teacher_lectures(teacher_subject_class_assignment, teacher_max_lectures)
    if reduced:
        print("Some assignments were reduced due to teacher slot limits:")
        for key, (old, new) in reduced.items():
            print(f"  {key}: {old} → {new}")

    return dict(
        teachers=teachers,
        classes=classes,
        subjects=subjects,
        class_teacher_map=class_teacher_map,
        teacher_subject_class_assignment=teacher_subject_class_assignment,
        lecture_slots=lecture_slots,
        subject_lecture_weekly_count=subject_lecture_weekly_count,
        teacher_max_lectures=teacher_max_lectures,
        teacher_availability=teacher_availability,
        breaks={},
        saturday_lecture_slots=saturday_lecture_slots,
    )


from ortools.sat.python import cp_model

def generate_school_timetable(
    teachers,
    classes,
    subjects,
    class_teacher_map,
    teacher_subject_class_assignment,
    lecture_slots,
    subject_lecture_weekly_count,
    teacher_max_lectures,
    teacher_availability,
    breaks,
    saturday_lecture_slots,
    custom_lunch_breaks=None,
    teacher_unavailability=None,
):
    print("🚦 Starting timetable generation with OR-Tools...")

    model = cp_model.CpModel()
    timetable_vars = {}
    all_days = list(lecture_slots.keys())

    teacher_id_to_idx = {tid: i for i, tid in enumerate(teachers)}
    subject_id_to_idx = {sid: i for i, sid in enumerate(subjects)}

    # DIAGNOSTIC SECTION: check for overloads before solving
    print("=== DIAGNOSTIC: Checking data consistency and overloads ===")
    class_overload = False
    teacher_overload = False

    for class_id in classes:
        total_required = sum(
            req_lectures
            for (teacher_id, subject_id, cid), req_lectures in teacher_subject_class_assignment.items()
            if cid == class_id
        )
        total_slots = sum(len(lecture_slots[day]) for day in all_days)
        if total_required > total_slots:
            print(f"❌ Class {class_id} OVERLOADED: Required lectures ({total_required}) > available slots ({total_slots})")
            class_overload = True
        else:
            print(f"✔️ Class {class_id}: Required lectures = {total_required}, Available slots = {total_slots}")

    for teacher_id in teachers:
        total_assigned = sum(
            req_lectures
            for (tid, subject_id, class_id), req_lectures in teacher_subject_class_assignment.items()
            if tid == teacher_id
        )
        max_allowed = teacher_max_lectures[teacher_id]
        if total_assigned > max_allowed:
            print(f"❌ Teacher {teacher_id} OVERLOADED: Assigned lectures ({total_assigned}) > max allowed ({max_allowed})")
            teacher_overload = True
        else:
            print(f"✔️ Teacher {teacher_id}: Assigned lectures = {total_assigned}, Max allowed = {max_allowed}")

    if class_overload or teacher_overload:
        print("\n❗ Infeasibility detected BEFORE solving. Please fix overloaded classes or teachers above.\n")

    print("⏳ Creating timetable variables for each class, day, slot...")
    for class_id in classes:
        for day in all_days:
            slots_today = lecture_slots[day]
            for slot_idx, slot_id in enumerate(slots_today):
                subject_var = model.NewIntVar(-1, len(subjects)-1, f'subj_c{class_id}_d{day}_s{slot_idx}')
                teacher_var = model.NewIntVar(-1, len(teachers)-1, f'teacher_c{class_id}_d{day}_s{slot_idx}')
                timetable_vars[(class_id, day, slot_idx)] = (subject_var, teacher_var)
    print(f"✔️ Created {len(timetable_vars)} timetable variables.")

    print("⏳ Adding assignment constraints for each teacher/subject/class...")
    for (teacher_id, subject_id, class_id), req_lectures in teacher_subject_class_assignment.items():
        count_bools = []
        teacher_idx = teacher_id_to_idx[teacher_id]
        subject_idx = subject_id_to_idx[subject_id]
        for day in all_days:
            for slot_idx in range(len(lecture_slots[day])):
                key = (class_id, day, slot_idx)
                if key not in timetable_vars:
                    continue
                subj_var, teach_var = timetable_vars[key]
                is_assigned = model.NewBoolVar(f"assigned_{class_id}_{day}_{slot_idx}_{teacher_id}_{subject_id}")
                model.Add(subj_var == subject_idx).OnlyEnforceIf(is_assigned)
                model.Add(subj_var != subject_idx).OnlyEnforceIf(is_assigned.Not())
                model.Add(teach_var == teacher_idx).OnlyEnforceIf(is_assigned)
                model.Add(teach_var != teacher_idx).OnlyEnforceIf(is_assigned.Not())
                count_bools.append(is_assigned)
        model.Add(sum(count_bools) == req_lectures)
        print(f"✔️ Constraint: teacher={teacher_id}, subject={subject_id}, class={class_id}, exactly {req_lectures} lectures.")

    print("⏳ Adding teacher weekly maximum constraints...")
    for teacher_id, max_lectures in teacher_max_lectures.items():
        teacher_idx = teacher_id_to_idx[teacher_id]
        teacher_bools = []
        for (class_id, day, slot_idx), (subj_var, teach_var) in timetable_vars.items():
            is_taught = model.NewBoolVar(f"teaching_{teacher_id}_{class_id}_{day}_{slot_idx}")
            model.Add(teach_var == teacher_idx).OnlyEnforceIf(is_taught)
            model.Add(teach_var != teacher_idx).OnlyEnforceIf(is_taught.Not())
            teacher_bools.append(is_taught)
        model.Add(sum(teacher_bools) <= max_lectures)
        print(f"✔️ Constraint: teacher={teacher_id} max {max_lectures} lectures.")

    print("⏳ Ensuring empty slots have at least one empty field (-1)...")
    for (class_id, day, slot_idx), (subj_var, teach_var) in timetable_vars.items():
        is_subj_empty = model.NewBoolVar(f"is_subj_empty_{class_id}_{day}_{slot_idx}")
        is_teach_empty = model.NewBoolVar(f"is_teach_empty_{class_id}_{day}_{slot_idx}")
        model.Add(subj_var == -1).OnlyEnforceIf(is_subj_empty)
        model.Add(subj_var != -1).OnlyEnforceIf(is_subj_empty.Not())
        model.Add(teach_var == -1).OnlyEnforceIf(is_teach_empty)
        model.Add(teach_var != -1).OnlyEnforceIf(is_teach_empty.Not())
        model.AddBoolOr([is_subj_empty, is_teach_empty])
    print("✔️ Empty slot constraints added.")

    print("⏳ Preventing teacher double-booking (one teacher per slot)...")
    # Check for teacher double-booking
    print("=== DIAGNOSTIC: Checking for potential teacher double-booking ===")
    slot_map = defaultdict(list)  # (day, slot_idx, teacher_id) -> list of (class_id, subject_id)

    for (teacher_id, subject_id, class_id), req_lectures in teacher_subject_class_assignment.items():
        for day in all_days:
            num_slots = len(lecture_slots[day])
            for slot_idx in range(num_slots):
                slot_map[(day, slot_idx, teacher_id)].append((class_id, subject_id))

    double_booking_found = False
    for key, assignments in slot_map.items():
        if len(assignments) > 1:
            day, slot_idx, teacher_id = key
            print(f"❌ Teacher {teacher_id} is potentially double-booked on {day} slot {slot_idx} for assignments: {assignments}")
            double_booking_found = True

    if double_booking_found:
        print("❗ INFEASIBLE: At least one teacher is assigned to multiple classes at the same time slot.")


    for day in all_days:
        for slot_idx in range(len(lecture_slots[day])):
            for teacher_idx in range(len(teachers)):
                teach_in_slot = []
                for class_id in classes:
                    key = (class_id, day, slot_idx)
                    if key not in timetable_vars:
                        continue
                    subj_var, teach_var = timetable_vars[key]
                    is_here = model.NewBoolVar(f"teach_{teacher_idx}_in_{class_id}_{day}_{slot_idx}")
                    model.Add(teach_var == teacher_idx).OnlyEnforceIf(is_here)
                    model.Add(teach_var != teacher_idx).OnlyEnforceIf(is_here.Not())
                    teach_in_slot.append(is_here)
                model.Add(sum(teach_in_slot) <= 1)
    print("✔️ Double-booking constraints done.")


    print("🚦 Solving model...")
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(f"🟢 Solver status: {solver.StatusName(status)}")

    result = []
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        print("✅ Solution found. Extracting assignments...")
        empty_slots = 0
        for (class_id, day, slot_idx), (subj_var, teach_var) in timetable_vars.items():
            subj_val = solver.Value(subj_var)
            teach_val = solver.Value(teach_var)
            if subj_val == -1 or teach_val == -1:
                empty_slots += 1
                continue  # empty slot, leave for manual fill
            subject_id = subjects[subj_val]
            teacher_id = teachers[teach_val]
            slot_id = lecture_slots[day][slot_idx]
            print(f"✅ Assign: class={class_id} day={day} slot={slot_id} subject={subject_id} teacher={teacher_id}")
            result.append({
                "class_id": class_id,
                "day": day,
                "slot_idx": slot_id,
                "subject_id": subject_id,
                "teacher_id": teacher_id,
            })
        print(f"✔️ Total empty slots: {empty_slots}")
        print(f"✔️ Total scheduled lectures: {len(result)}")
    else:
        print("❌ No feasible timetable found.")
        # Print likely reason
        if class_overload or teacher_overload:
            print("❗ INFEASIBLE due to overloads above (see ❌ lines).")
        else:
            print("❗ INFEASIBLE for another reason: e.g., double-booking or not enough available teachers/slots for the required assignments.")

    print("🏁 Timetable generation complete.")
    return result