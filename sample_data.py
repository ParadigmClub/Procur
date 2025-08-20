from app import app, db, User, Event, EventRegistration, Schedule
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_sample_data():
    with app.app_context():

        db.create_all()
        
        print("Creating sample data...")
        

        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Sample data already exists. Skipping creation.")
            return
        

        users = [
            User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                school='Ahlcon International School'
            ),
            User(
                username='coordinator1',
                email='coord1@school.com',
                password_hash=generate_password_hash('coord123'),
                role='coordinator',
                school='Ahlcon International School'
            ),
            User(
                username='coordinator2',
                email='coord2@school.com',
                password_hash=generate_password_hash('coord123'),
                role='coordinator',
                school='Ahlcon International School'
            ),
            User(
                username='student1',
                email='student1@school.com',
                password_hash=generate_password_hash('student123'),
                role='participant',
                school='Ahlcon International School'
            ),
            User(
                username='student2',
                email='student2@school.com',
                password_hash=generate_password_hash('student123'),
                role='participant',
                school='Ahlcon International School'
            ),
            User(
                username='teacher1',
                email='teacher1@school.com',
                password_hash=generate_password_hash('teacher123'),
                role='participant',
                school='Ahlcon International School'
            ),
            User(
                username='teacher2',
                email='teacher2@school.com',
                password_hash=generate_password_hash('teacher123'),
                role='participant',
                school='Ahlcon International School'
            )
        ]
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users")
        

        now = datetime.now()
        
        events = [
            Event(
                title='Inter-School Science Fair 2025',
                description='Annual science fair showcasing innovative projects from students across the district. Categories include Physics, Chemistry, Biology, and Engineering. Winners will represent the district at the state level.',
                event_date=now + timedelta(days=30),
                location='Central School District Auditorium',
                max_participants=150,
                registration_deadline=now + timedelta(days=20),
                status='upcoming',
                created_by=2,  # coordinator1
                category='technical'
            ),
            Event(
                title='District Sports Championship',
                description='Annual inter-school sports competition featuring basketball, volleyball, and track events. Open to all high school students. Individual and team awards will be presented.',
                event_date=now + timedelta(days=45),
                location='District Sports Complex',
                max_participants=200,
                registration_deadline=now + timedelta(days=35),
                status='upcoming',
                created_by=2,  # coordinator1
                category='sports'
            ),
            Event(
                title='Cultural Arts Festival',
                description='Celebration of diverse cultures through music, dance, art, and drama performances. Students from all schools are invited to showcase their talents and cultural heritage.',
                event_date=now + timedelta(days=60),
                location='Community Arts Center',
                max_participants=100,
                registration_deadline=now + timedelta(days=50),
                status='upcoming',
                created_by=3,  # coordinator2
                category='cultural'
            ),
            Event(
                title='Academic Quiz Bowl',
                description='Intellectual competition testing knowledge in various subjects including History, Literature, Science, and Current Events. Teams of 4 students per school.',
                event_date=now + timedelta(days=75),
                location='Lincoln High School Library',
                max_participants=80,
                registration_deadline=now + timedelta(days=65),
                status='upcoming',
                created_by=3,  # coordinator2
                category='academic'
            ),
            Event(
                title='Creative Writing Workshop',
                description='Interactive workshop led by published authors and educators. Students will learn creative writing techniques and have the opportunity to share their work.',
                event_date=now + timedelta(days=15),
                location='Roosevelt Middle School',
                max_participants=50,
                registration_deadline=now + timedelta(days=10),
                status='upcoming',
                created_by=2,  # coordinator1
                category='literary'
            )
        ]
        
        for event in events:
            db.session.add(event)
        db.session.commit()
        print(f"Created {len(events)} events")
        

        schedules = [
            Schedule(
                event_id=1,  # Science Fair
                activity='Registration and Setup',
                start_time=events[0].event_date.replace(hour=8, minute=0),
                end_time=events[0].event_date.replace(hour=9, minute=0),
                location='Main Hall',
                description='Participants arrive and set up their projects'
            ),
            Schedule(
                event_id=1,
                activity='Judging Round 1',
                start_time=events[0].event_date.replace(hour=9, minute=0),
                end_time=events[0].event_date.replace(hour=11, minute=0),
                location='Various Classrooms',
                description='Initial judging of all projects'
            ),
            Schedule(
                event_id=1,
                activity='Lunch Break',
                start_time=events[0].event_date.replace(hour=11, minute=0),
                end_time=events[0].event_date.replace(hour=12, minute=0),
                location='Cafeteria',
                description='Lunch provided for all participants'
            ),
            Schedule(
                event_id=1,
                activity='Final Judging',
                start_time=events[0].event_date.replace(hour=12, minute=0),
                end_time=events[0].event_date.replace(hour=2, minute=0),
                location='Auditorium',
                description='Final round judging and awards ceremony'
            ),
            Schedule(
                event_id=2,  # Sports Championship
                activity='Opening Ceremony',
                start_time=events[1].event_date.replace(hour=8, minute=30),
                end_time=events[1].event_date.replace(hour=9, minute=0),
                location='Main Field',
                description='Welcome and rules overview'
            ),
            Schedule(
                event_id=2,
                activity='Basketball Tournament',
                start_time=events[1].event_date.replace(hour=9, minute=0),
                end_time=events[1].event_date.replace(hour=12, minute=0),
                location='Indoor Gym',
                description='Basketball competition'
            ),
            Schedule(
                event_id=2,
                activity='Volleyball Tournament',
                start_time=events[1].event_date.replace(hour=1, minute=0),
                end_time=events[1].event_date.replace(hour=4, minute=0),
                location='Outdoor Courts',
                description='Volleyball competition'
            )
        ]
        
        for schedule in schedules:
            db.session.add(schedule)
        db.session.commit()
        print(f"Created {len(schedules)} schedule items")
        

        registrations = [
            EventRegistration(
                event_id=1,  # Science Fair
                user_id=4,   # student1
                status='confirmed'
            ),
            EventRegistration(
                event_id=1,  # Science Fair
                user_id=5,   # student2
                status='confirmed'
            ),
            EventRegistration(
                event_id=1,  # Science Fair
                user_id=6,   # teacher1
                status='confirmed'
            ),
            EventRegistration(
                event_id=2,  # Sports Championship
                user_id=4,   # student1
                status='confirmed'
            ),
            EventRegistration(
                event_id=2,  # Sports Championship
                user_id=7,   # teacher2
                status='confirmed'
            ),
            EventRegistration(
                event_id=3,  # Cultural Arts Festival
                user_id=5,   # student2
                status='confirmed'
            ),
            EventRegistration(
                event_id=4,  # Academic Quiz Bowl
                user_id=6,   # teacher1
                status='confirmed'
            ),
            EventRegistration(
                event_id=5,  # Creative Writing Workshop
                user_id=4,   # student1
                status='confirmed'
            )
        ]
        
        for registration in registrations:
            db.session.add(registration)
        db.session.commit()
        print(f"Created {len(registrations)} registrations")
        
        print("\nSample data creation completed successfully!")
        print("\nDefault login credentials:")
        print("Admin: admin / admin123")
        print("Coordinator: coordinator1 / coord123")
        print("Student: student1 / student123")
        print("\nThe application is ready to use!")

if __name__ == '__main__':
    create_sample_data()
