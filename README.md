# Procur


Simplicity of Flask + Reliability of SQL = **Procurator**
> Interschool Event Management Platform

- **Scoped Authority** w/roles -> Admin, Coordinator, Participant
- **Event Management**: -> Create, edit, and manage interschool events
- **Inbuilt Registration System**: -> Ez Registration process cuz google forms are a nightmare ong
- **Scheduling**: -> We beating notion with this one
- **Real-time Stuff**: -> Live status updates and notifications cause you can get busy 
- **Responsive(OFC)**: -> Its 2025 if it's not responsive i ain't using it


- **Admin**: Full system access, user management, event oversight
- **Coordinator**: Event creation and management, participant coordination
- **Participant**: Event browsing, registration, personal dashboard


> Initially we developed this for interschool tech events but since arnav my goat gave us extra days we said why not add more types of events
- Sports competitions (Badminton , Basketball or Olympic Style Tourneys)
- Academic competitions (Math Fiesta)
- Cultural events (Synergy type events with hybrids)
- Technical exhibitions (S.T.E.A.M Workshops and Science Fairs)
- Literary competitions (My English teacher would like this)
- Art & Design showcases ()
- Music and Dance performances (Includes stuff like annual days)
- Drama and Theater (We apparently have a different?)


## Tech
- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Web**: Vanilla HTML + DaisyUI


## Requirements
- Python 3.8 or higher
- pip (Python package installer)


### Admin Credentials

- **Username**: paradigm
- **Password**: Paradigm123

1. **User Management**: Access admin panel to manage user roles and permissions
2. **System Oversight**: Monitor all events, registrations, and system statistics
3. **Event Control**: Approve, modify, or cancel events as needed
1. **Event Creation**: Create new events with detailed information
2. **Participant Management**: Monitor registrations and manage participant lists
3. **Schedule Planning**: Set up detailed event timelines and activities


1. **Event Discovery**: Browse available events by category and status
2. **Registration**: Register for events within deadlines and capacity limits
3. **Personal Dashboard**: Track registered events and personal schedule


### Setup Environment
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///events.db
FLASK_ENV=development
```


### Security

- Passwords are hashed using Werkzeug
- Every type of input validation is implemented
- CSRF protection is implemented
- Also, in case the event head goes rogue, permissions are scoped


### Why the name

Procur comes from Procurator which means "manager". Internally developed as SparkHub it was renamed to sound like a professional and new event management tool.

---






