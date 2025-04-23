from typing import List, Optional
from datetime import date

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, Relationship, select

# ---------- MODELS & SCHEMAS ----------

class ClassroomStudent(SQLModel, table=True):
    classroom_id: Optional[int] = Field(
        default=None, foreign_key="classroom.id", primary_key=True
    )
    student_id: Optional[int] = Field(
        default=None, foreign_key="student.id", primary_key=True
    )

class StudentBase(SQLModel):
    name: str
    contact_number: str
    dob: date

class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    classrooms: List["Classroom"] = Relationship(
        back_populates="students", link_model=ClassroomStudent
    )
    issues: List["Issue"] = Relationship(back_populates="student")
    results: List["ExamResult"] = Relationship(back_populates="student")
    fees: List["ExamFee"] = Relationship(back_populates="student")

class StaffBase(SQLModel):
    name: str
    contact_number: str
    dob: date

class Staff(StaffBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ClassroomBase(SQLModel):
    class_name: str
    std: str
    sec: str
    class_teacher: str

class Classroom(ClassroomBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    students: List[Student] = Relationship(
        back_populates="classrooms", link_model=ClassroomStudent
    )

class BookBase(SQLModel):
    title: str
    author: str
    isbn: str
    total_copies: int

class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    available_copies: int = Field(default=0)
    issues: List["Issue"] = Relationship(back_populates="book")

class Issue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    book_id: int = Field(foreign_key="book.id")
    issue_date: date = Field(default_factory=date.today)
    return_date: Optional[date] = None

    student: Student = Relationship(back_populates="issues")
    book: Book = Relationship(back_populates="issues")

class ExamResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    exam_name: str
    marks_obtained: float
    max_marks: float

    student: Student = Relationship(back_populates="results")

class ExamFee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    amount: float
    due_date: date
    paid: bool = Field(default=False)

    student: Student = Relationship(back_populates="fees")


class ClassroomRead(ClassroomBase):
    id: int

class BookRead(BookBase):
    id: int
    available_copies: int

class IssueRead(SQLModel):
    id: int
    issue_date: date
    return_date: Optional[date]
    book: BookRead

class ExamResultRead(SQLModel):
  
    exam_name: str
    marks_obtained: float
    max_marks: float

class ExamFeeRead(SQLModel):
    id: int
    amount: float
    due_date: date
    paid: bool

class StudentRead(StudentBase):
    id: int
    classrooms: List[ClassroomRead]
    issues: List[IssueRead]
    results: List[ExamResultRead]
    fees: List[ExamFeeRead]


# ---------- DATABASE SETUP ----------

DATABASE_URL = "sqlite:///./school.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ---------- FASTAPI APP ----------

app = FastAPI(on_startup=[create_db_and_tables])

# ---------- STUDENT CRUD ----------

@app.post("/students/", response_model=Student)
def create_student(student: StudentBase, session: Session = Depends(get_session)):
    db_student = Student(**student.dict())
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[Student])
def list_students(session: Session = Depends(get_session)):
    return session.exec(select(Student)).all()

@app.get("/students/{student_id}", response_model=StudentRead)
def get_student(student_id: int, session: Session = Depends(get_session)):
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentBase, session: Session = Depends(get_session)):
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, val in student.dict().items():
        setattr(db_student, key, val)
    session.commit()
    session.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, session: Session = Depends(get_session)):
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    session.delete(db_student)
    session.commit()

# ---------- STAFF CRUD ----------

@app.post("/staff/", response_model=Staff)
def create_staff(staff: StaffBase, session: Session = Depends(get_session)):
    db_staff = Staff(**staff.dict())
    session.add(db_staff)
    session.commit()
    session.refresh(db_staff)
    return db_staff

@app.get("/staff/", response_model=List[Staff])
def list_staff(session: Session = Depends(get_session)):
    return session.exec(select(Staff)).all()

@app.get("/staff/{staff_id}", response_model=Staff)
def get_staff(staff_id: int, session: Session = Depends(get_session)):
    db_staff = session.get(Staff, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff

@app.put("/staff/{staff_id}", response_model=Staff)
def update_staff(staff_id: int, staff: StaffBase, session: Session = Depends(get_session)):
    db_staff = session.get(Staff, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for key, val in staff.dict().items():
        setattr(db_staff, key, val)
    session.commit()
    session.refresh(db_staff)
    return db_staff

@app.delete("/staff/{staff_id}", status_code=204)
def delete_staff(staff_id: int, session: Session = Depends(get_session)):
    db_staff = session.get(Staff, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    session.delete(db_staff)
    session.commit()

# ---------- CLASSROOMS ----------

@app.post("/classrooms/", response_model=Classroom)
def create_classroom(classroom: ClassroomBase, session: Session = Depends(get_session)):
    db_class = Classroom(**classroom.dict())
    session.add(db_class)
    session.commit()
    session.refresh(db_class)
    return db_class

@app.get("/classrooms/", response_model=List[Classroom])
def list_classrooms(session: Session = Depends(get_session)):
    return session.exec(select(Classroom)).all()

@app.post("/classrooms/{class_id}/add_student/{student_id}", response_model=Classroom)
def add_student_to_class(class_id: int, student_id: int, session: Session = Depends(get_session)):
    db_class = session.get(Classroom, class_id)
    db_student = session.get(Student, student_id)
    if not db_class or not db_student:
        raise HTTPException(status_code=404, detail="Class or Student not found")
    if db_student in db_class.students:
        raise HTTPException(status_code=400, detail="Student already in class")
    db_class.students.append(db_student)
    session.commit()
    session.refresh(db_class)
    return db_class

@app.post("/classrooms/{class_id}/remove_student/{student_id}", response_model=Classroom)
def remove_student_from_class(class_id: int, student_id: int, session: Session = Depends(get_session)):
    db_class = session.get(Classroom, class_id)
    db_student = session.get(Student, student_id)
    if not db_class or not db_student:
        raise HTTPException(status_code=404, detail="Class or Student not found")
    if db_student not in db_class.students:
        raise HTTPException(status_code=400, detail="Student not in class")
    db_class.students.remove(db_student)
    session.commit()
    session.refresh(db_class)
    return db_class

@app.get("/classrooms/{class_id}/students", response_model=List[Student])
def get_class_students(class_id: int, session: Session = Depends(get_session)):
    db_class = session.get(Classroom, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class.students

# ---------- LIBRARY ----------

@app.post("/books/", response_model=Book)
def add_book(book: BookBase, session: Session = Depends(get_session)):
    db_book = Book(**book.dict(), available_copies=book.total_copies)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[Book])
def list_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.post("/issues/", response_model=Issue)
def issue_book(issue: Issue, session: Session = Depends(get_session)):
    db_book = session.get(Book, issue.book_id)
    if not db_book or db_book.available_copies < 1:
        raise HTTPException(status_code=400, detail="Book unavailable")
    db_book.available_copies -= 1
    session.add(db_book)
    session.add(issue)
    session.commit()
    session.refresh(issue)
    return issue

@app.post("/returns/{issue_id}", response_model=Issue)
def return_book(issue_id: int, session: Session = Depends(get_session)):
    db_issue = session.get(Issue, issue_id)
    if not db_issue or db_issue.return_date:
        raise HTTPException(status_code=400, detail="Invalid return")
    db_issue.return_date = date.today()
    db_book = session.get(Book, db_issue.book_id)
    db_book.available_copies += 1
    session.add_all([db_issue, db_book])
    session.commit()
    session.refresh(db_issue)
    return db_issue

@app.get("/students/{student_id}/issues", response_model=List[Issue])
def student_issues(student_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Issue).where(Issue.student_id == student_id)).all()

# ---------- EXAM RESULTS ----------

@app.post("/results/", response_model=ExamResult)
def add_result(result: ExamResult, session: Session = Depends(get_session)):
    session.add(result)
    session.commit()
    session.refresh(result)
    return result

@app.get("/results/", response_model=List[ExamResult])
def list_results(session: Session = Depends(get_session)):
    return session.exec(select(ExamResult)).all()

@app.get("/students/{student_id}/results", response_model=List[ExamResult])
def get_results(student_id: int, session: Session = Depends(get_session)):
    return session.exec(select(ExamResult).where(ExamResult.student_id == student_id)).all()

@app.get("/results/{result_id}", response_model=ExamResult)
def get_result(result_id: int, session: Session = Depends(get_session)):
    db_result = session.get(ExamResult, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="Result not found")
    return db_result

@app.delete("/results/{result_id}", status_code=204)
def delete_result(result_id: int, session: Session = Depends(get_session)):
    db_result = session.get(ExamResult, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="Result not found")
    session.delete(db_result)
    session.commit()

# ---------- EXAM FEES ----------

@app.post("/fees/", response_model=ExamFee)
def add_fee(fee: ExamFee, session: Session = Depends(get_session)):
    session.add(fee)
    session.commit()
    session.refresh(fee)
    return fee

@app.get("/students/{student_id}/fees", response_model=List[ExamFee])
def get_fees(student_id: int, session: Session = Depends(get_session)):
    return session.exec(select(ExamFee).where(ExamFee.student_id == student_id)).all()

@app.get("/fees/", response_model=List[ExamFee])
def list_fees(session: Session = Depends(get_session)):
    return session.exec(select(ExamFee)).all()

@app.get("/fees/{fee_id}", response_model=ExamFee)
def get_fee(fee_id: int, session: Session = Depends(get_session)):
    db_fee = session.get(ExamFee, fee_id)
    if not db_fee:
        raise HTTPException(status_code=404, detail="Fee not found")
    return db_fee

@app.put("/fees/{fee_id}", response_model=ExamFee)
def update_fee(fee_id: int, fee: ExamFee, session: Session = Depends(get_session)):
    db_fee = session.get(ExamFee, fee_id)
    if not db_fee:
        raise HTTPException(status_code=404, detail="Fee not found")
    for key, val in fee.dict(exclude_unset=True).items():
        setattr(db_fee, key, val)
    session.commit()
    session.refresh(db_fee)
    return db_fee

@app.delete("/fees/{fee_id}", status_code=204)
def delete_fee(fee_id: int, session: Session = Depends(get_session)):
    db_fee = session.get(ExamFee, fee_id)
    if not db_fee:
        raise HTTPException(status_code=404, detail="Fee not found")
    session.delete(db_fee)
    session.commit()
