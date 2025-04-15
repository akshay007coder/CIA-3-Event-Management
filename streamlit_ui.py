import streamlit as st
import pymysql
import bcrypt
from datetime import datetime, time, date, timedelta
from collections import defaultdict
import calendar

# Apply Custom Styling
st.markdown(
    """
    <p style="
        text-align: center; 
        font-size: 60px; 
        font-weight: bold; 
        color: white; 
        text-shadow: 6px 6px 12px rgba(0, 0, 0, 0.8); 
        margin-bottom: 20px;">
        Event Management System
    </p>
    """,
    unsafe_allow_html=True, 
)

def get_db_connection(): 
    return pymysql.connect( 
        host="localhost", 
        user="root", 
        password="akshay_babu_007",
        database="event_management",
        autocommit=True, 
        cursorclass=pymysql.cursors.DictCursor 
    )

# ✅ Initialize session state
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False 
    st.session_state.user_id = None 
    st.session_state.role = None 

# ✅ Sidebar Navigation
if st.session_state.logged_in:
    if st.session_state.role == "organizer":
        menu = st.sidebar.radio("Organizer Panel", ["Home", "Create Event", "View Events", "Update Event", "Cancel Event", "Logout"], key="organizer_menu")
    elif st.session_state.role == "attendee":
        menu = st.sidebar.radio("Attendee Panel", ["Home", "View Events", "Buy Ticket", "View My Tickets", "Logout"], key="user_menu")
    elif st.session_state.role == "participant":
        menu = st.sidebar.radio("Participant Panel", ["Home", "View Events", "Register for Event", "View My Registrations", "Logout"], key="participant_menu")
    else:
        st.error("⚠️ Invalid role detected. Please log in again.")
        menu = "Logout"
else:
    menu = st.sidebar.radio("Navigation", ["Home", "Register", "Login"], key="nav_menu")

# ✅ Home Page (Show active events with posters)
if menu == "Home":
    st.subheader("🎉 Upcoming Events")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT title, location, date, time, description, poster_path FROM events WHERE status = 'active'")
            events = cursor.fetchall()

        if not events:
            st.info("📢 No upcoming events at the moment.")
        else:
            for event in events:
                event_date = event['date'].strftime("%Y-%m-%d") if isinstance(event['date'], datetime) else event['date']
                event_time = event['time'].strftime("%I:%M %p") if isinstance(event['time'], time) else event['time']
                
                # Create two columns: poster on left, details on right
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if event['poster_path']:
                        try:
                            st.image(event['poster_path'], use_container_width=True)
                        except FileNotFoundError:
                            st.warning("⚠️ Poster not found.")
                    else:
                        st.write("🖼️ No poster available.")
                
                with col2:
                    st.markdown(
                        f"""
                        <div style="padding: 10px;">
                            <h3 style="color: white;">{event['title']}</h3>
                            <p style="color: white;">📍 {event['location']} | 📅 {event_date} | 🕒 {event_time}</p>
                            <p style="color: white;">📝 {event['description']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("<hr>", unsafe_allow_html=True)  # Separator between events
    except Exception as e:
        st.error(f"⚠️ Error fetching events: {str(e)}")
    finally:
        conn.close()

# ✅ User Login
if menu == "Login": 
    st.subheader("🔓 Login") 
    email = st.text_input("Email") 
    password = st.text_input("Password", type="password") 
    
    if st.button("Login"): 
        if email and password: 
            try:
                conn = get_db_connection() 
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, password, role FROM users WHERE email = %s", (email,)) 
                    user = cursor.fetchone() 

                    if user and bcrypt.checkpw(password.encode(), user['password'].encode()): 
                        st.session_state.logged_in = True 
                        st.session_state.user_id = user["id"] 
                        st.session_state.role = user["role"] 
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun() 
                    else:
                        st.error("❌ Invalid credentials!")
            except Exception as e: 
                st.error(f"⚠️ Error: {str(e)}") 
            finally: 
                conn.close()
        else:
            st.error("❌ Please enter both email and password!")

# ✅ User Registration
if menu == "Register":
    st.subheader("🔑 Register")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Attendee", "Organizer", "Participant"])  # Updated

    if st.button("Register"):
        if name and email and password:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_pw, role.lower())
                    )
                st.success("✅ Registration successful! Please login.")
            except pymysql.err.IntegrityError:
                st.error("❌ Email already exists!")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
            finally:
                conn.close()
        else:
            st.error("❌ All fields are required!")

# ✅ Create Event (for organizers only)
if menu == "Create Event":
    if st.session_state.role != "organizer":
        st.error("❌ You must be an organizer to create an event.")
    else:
        st.subheader("📝 Create New Event")

        title = st.text_input("Event Title")

        predefined_locations = [
            "Main Auditorium", "Mini Auditorium", "Synergy Square", "Gazebo",
            "B-block Basement", "Discussion Room", "Finance Lab", "Seminar Hall"
        ]
        location = st.selectbox("Select Location", predefined_locations)

        event_date = st.date_input("Event Date")
        event_time = st.time_input("Event Time")
        description = st.text_area("Description")
        capacity = st.number_input("Total Capacity", min_value=1, step=1)

        vip_price = st.number_input("VIP Ticket Price", min_value=0.0, step=0.01)
        general_price = st.number_input("General Ticket Price", min_value=0.0, step=0.01)

        vip_tickets = int(capacity * 0.3)
        general_tickets = capacity - vip_tickets

        st.write(f"🎟️ VIP Tickets: {vip_tickets}, General Tickets: {general_tickets}")

        if st.button("Create Event"):
            user_id = st.session_state.get("user_id")
            current_date = date.today()

            if not user_id:
                st.error("⚠️ User ID not found. Please log in again.")
            elif title and location and event_date and event_time and description and capacity and vip_price and general_price:
                if event_date <= current_date:
                    st.error("❌ Cannot take this event date")
                else:
                    try:
                        conn = get_db_connection()
                        with conn.cursor() as cursor:
                            # 🔍 Check for location conflict regardless of user
                            cursor.execute("""
                                SELECT COUNT(*) FROM events
                                WHERE location = %s AND date = %s AND time = %s AND status = 'active'
                            """, (location, event_date, event_time))
                            conflict_count = cursor.fetchone()[0]

                            if conflict_count > 0:
                                st.error("❌ This location is already booked for the selected date and time.")
                            else:
                                cursor.execute("""
                                    INSERT INTO events 
                                    (title, location, date, time, description, capacity, vip_tickets, general_tickets, vip_price, general_price, user_id, status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
                                """, (
                                    title, location, event_date, event_time, description, capacity,
                                    vip_tickets, general_tickets, vip_price, general_price, user_id
                                ))
                                conn.commit()
                                st.success("✅ Event created successfully!")

                    except Exception as e:
                        st.error(f"⚠️ Error creating event: {str(e)}")
                    finally:
                        conn.close()
            else:
                st.error("❌ All fields are required!")

def get_month_dates(year, month):
    """Returns all dates in a given month"""
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]

# ✅ View Events (Only show active events)
if menu == "View Events":
    st.subheader("🎟 Available Events")

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM events WHERE status = 'active'")
            events = cursor.fetchall()

            if not events:
                st.info("No upcoming events found.")
            elif st.session_state.role == "organizer":
                st.subheader("📅 Monthly Calendar View")

                # Month selector
                today = datetime.today()
                current_month = today.month
                current_year = today.year

                col1, col2 = st.columns(2)
                with col1:
                    selected_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=current_month - 1)
                with col2:
                    selected_year = st.selectbox("Select Year", list(range(current_year, current_year + 2)))

                month_index = list(calendar.month_name).index(selected_month)
                month_dates = get_month_dates(selected_year, month_index)

                # Group events by date
                calendar_map = defaultdict(list)
                for event in events:
                    event_date = event['date']
                    if isinstance(event_date, str):
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                    elif isinstance(event_date, datetime):
                        event_date = event_date.date()

                    event_time = event['time']
                    if isinstance(event_time, str):
                        try:
                            event['time'] = datetime.strptime(event_time, "%H:%M:%S").time()
                        except:
                            event['time'] = datetime.strptime(event_time, "%H:%M").time()
                    elif isinstance(event_time, datetime):
                        event['time'] = event_time.time()

                    calendar_map[event_date].append(event)

                # Show in calendar grid (7 days per row)
                weeks = [month_dates[i:i + 7] for i in range(0, len(month_dates), 7)]

                for week in weeks:
                    cols = st.columns(7)
                    for i, day in enumerate(week):
                        with cols[i]:
                            st.markdown(f"### {day.strftime('%d %a')}")
                            if calendar_map.get(day):
                                for ev in sorted(calendar_map[day], key=lambda x: x['time']):
                                    ev_time = ev['time'].strftime("%I:%M %p") if isinstance(ev['time'], time) else str(ev['time'])
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #e8f0fe; border-left: 5px solid #4285f4; padding: 8px; margin-bottom: 10px; border-radius: 6px; color: #0b5394;">
                                            <strong>{ev['title']}</strong><br>
                                            🕒 {ev_time}<br>
                                            📍 {ev['location']}<br>
                                            <span style="font-size: small;">{ev['description']}</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.markdown("<span style='color: gray;'>No events</span>", unsafe_allow_html=True)

            else:
                st.subheader("📋 Event List for Attendees")
                for event in events:
                    event_date = event['date']
                    if isinstance(event_date, str):
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                    elif isinstance(event_date, datetime):
                        event_date = event_date.date()

                    event_time = event['time']
                    if isinstance(event_time, str):
                        try:
                            event_time = datetime.strptime(event_time, "%H:%M:%S").time()
                        except:
                            event_time = datetime.strptime(event_time, "%H:%M").time()
                    elif isinstance(event_time, datetime):
                        event_time = event_time.time()

                    st.markdown(
                        f"""
                        <div style="background-color: #e8f0fe; border-left: 5px solid #4285f4; padding: 8px; margin-bottom: 10px; border-radius: 6px; color: #0b5394;">
                            <strong>{event['title']}</strong><br>
                            🕒 {event_time}<br>
                            📍 {event['location']}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f"⚠️ Error fetching events: {str(e)}")
    finally:
        if conn:
            conn.close()

# ✅ Register for Event (Only for Participants, only active events)
if menu == "Register for Event" and st.session_state.role == "participant":
    st.subheader("📋 Register for Event")
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM events WHERE status = 'active'")
        events = cursor.fetchall()
    conn.close()

    if not events:
        st.info("📢 No active events available.")
    else:
        event_options = {event['title']: event for event in events}
        selected_event = st.selectbox("Select Event", list(event_options.keys()))
        event = event_options[selected_event]

        # Check if already registered
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM registrations WHERE user_id = %s AND event_id = %s",
                (st.session_state.user_id, event['id'])
            )
            already_registered = cursor.fetchone()['count'] > 0
        conn.close()

        if already_registered:
            st.warning("⚠️ You are already registered for this event.")
        else:
            st.write(f"Event: {event['title']} | 📍 {event['location']} | 📅 {event['date']} | 🕒 {event['time']}")
            if st.button("Register"):
                try:
                    conn = get_db_connection()
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)",
                            (st.session_state.user_id, event['id'])
                        )
                        conn.commit()
                        st.success(f"✅ Successfully registered for {event['title']}!")
                except pymysql.err.IntegrityError:
                    st.error("⚠️ You are already registered for this event.")
                except Exception as e:
                    st.error(f"⚠️ Error registering for event: {str(e)}")
                finally:
                    conn.close()

st.cache_data.clear()
st.experimental_rerun()

# ✅ View Events (Only show active events)
if menu == "View Events":
    st.subheader("🎟 Available Events")

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM events WHERE status = 'active'")
            events = cursor.fetchall()

            if not events:
                st.info("No upcoming events found.")
            elif st.session_state.role == "organizer":
                st.subheader("📅 Monthly Calendar View")

                today = datetime.today()
                current_month = today.month
                current_year = today.year

                col1, col2 = st.columns(2)
                with col1:
                    selected_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=current_month - 1)
                with col2:
                    selected_year = st.selectbox("Select Year", list(range(current_year, current_year + 2)))

                month_index = list(calendar.month_name).index(selected_month)
                month_dates = get_month_dates(selected_year, month_index)

                calendar_map = defaultdict(list)
                for event in events:
                    event_date = event['date']
                    if isinstance(event_date, str):
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                    elif isinstance(event_date, datetime):
                        event_date = event_date.date()

                    event_time = event['time']
                    if isinstance(event_time, str):
                        try:
                            event['time'] = datetime.strptime(event_time, "%H:%M:%S").time()
                        except:
                            event['time'] = datetime.strptime(event_time, "%H:%M").time()
                    elif isinstance(event_time, datetime):
                        event['time'] = event_time.time()

                    # ❌ Remove description so it's not used anywhere
                    event.pop('description', None)

                    calendar_map[event_date].append(event)

                weeks = [month_dates[i:i + 7] for i in range(0, len(month_dates), 7)]

                for week in weeks:
                    cols = st.columns(7)
                    for i, day in enumerate(week):
                        with cols[i]:
                            st.markdown(f"### {day.strftime('%d %a')}")
                            if calendar_map.get(day):
                                for ev in sorted(calendar_map[day], key=lambda x: x['time']):
                                    ev_time = ev['time'].strftime("%I:%M %p") if isinstance(ev['time'], time) else str(ev['time'])
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #e8f0fe; 
                                                    border-left: 5px solid #4285f4; 
                                                    padding: 12px; 
                                                    margin-bottom: 12px; 
                                                    border-radius: 10px; 
                                                    color: #0b5394;
                                                    width: 95%;
                                                    max-width: 220px;
                                                    min-width: 150px;
                                                    font-size: 14px;">
                                            <strong style="font-size: 16px;">{ev['title']}</strong><br>
                                            🕒 {ev_time}<br>
                                            📍 {ev['location']}
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.markdown("<span style='color: gray;'>No events</span>", unsafe_allow_html=True)

            else:
                st.subheader("📋 Event List for Attendees")
                for event in events:
                    event_date = event['date']
                    if isinstance(event_date, str):
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                    elif isinstance(event_date, datetime):
                        event_date = event_date.date()

                    event_time = event['time']
                    if isinstance(event_time, str):
                        try:
                            event_time = datetime.strptime(event_time, "%H:%M:%S").time()
                        except:
                            event_time = datetime.strptime(event_time, "%H:%M").time()
                    elif isinstance(event_time, datetime):
                        event_time = event_time.time()

                    # ❌ Remove description
                    event.pop('description', None)

                    st.markdown(
                        f"""
                        <div style="background-color: #e8f0fe; 
                                    border-left: 5px solid #4285f4; 
                                    padding: 10px; 
                                    margin-bottom: 12px; 
                                    border-radius: 8px; 
                                    color: #0b5394;
                                    width: 100%;
                                    font-size: 14px;">
                            <strong style="font-size: 16px;">{event['title']}</strong><br>
                            🕒 {event_time}<br>
                            📍 {event['location']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f"⚠️ Error fetching events: {str(e)}")
    finally:
        if conn:
            conn.close()

# ✅ View My Registrations (Only for Participants)
if menu == "View My Registrations" and st.session_state.role == "participant":
    st.subheader("📋 My Registered Events")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.*, e.title, e.location, e.date, e.time, e.status 
                FROM registrations r 
                JOIN events e ON r.event_id = e.id 
                WHERE r.user_id = %s
            """, (st.session_state.user_id,))
            registrations = cursor.fetchall()

            if not registrations:
                st.info("📢 You have not registered for any events yet.")
            else:
                for reg in registrations:
                    event_date = reg['date'].strftime("%Y-%m-%d") if isinstance(reg['date'], datetime) else reg['date']
                    event_time = reg['time'].strftime("%I:%M %p") if isinstance(reg['time'], time) else reg['time']
                    status_note = "(Event Canceled)" if reg['status'] == 'canceled' else ""
                    
                    st.markdown(
                        f"""
                        <div style="background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px gray; margin-bottom: 10px; color: black;">
                            <h2 style="color: black;">{reg['title']} {status_note}</h2>
                            <p style="color: black;">📍 {reg['location']} | 📅 {event_date} | 🕒 {event_time}</p>
                            <p style="color: black;">📋 Registered on: {reg['registration_date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.error(f"⚠️ Error fetching registered events: {str(e)}")
    finally:
        conn.close()

# ✅ Buy Tickets (Only for Attendees, only active events)
if menu == "Buy Ticket" and st.session_state.role == "attendee":
    st.subheader("🎟 Book Your Ticket")
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM events WHERE status = 'active'")
        events = cursor.fetchall()
    conn.close()

    if not events:
        st.info("📢 No active events available.")
    else:
        event_options = {event['title']: event for event in events}
        selected_event = st.selectbox("Select Event", list(event_options.keys()))
        event = event_options[selected_event]
        
        # Display remaining tickets and input fields side by side
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Remaining VIP Tickets: {event['vip_tickets']} (Price: ${event['vip_price']:.2f})")
            vip_tickets = st.number_input("VIP Tickets", min_value=0, max_value=event['vip_tickets'], step=1, key="vip_input")
        with col2:
            st.write(f"Remaining General Tickets: {event['general_tickets']} (Price: ${event['general_price']:.2f})")
            general_tickets = st.number_input("General Tickets", min_value=0, max_value=event['general_tickets'], step=1, key="general_input")

        total_tickets = vip_tickets + general_tickets
        total_cost = (vip_tickets * event['vip_price']) + (general_tickets * event['general_price'])
        if total_tickets > 0:
            st.write(f"Total Cost: ${total_cost:.2f}")

        if st.button("Book Ticket"):
            if total_tickets == 0: 
                st.warning("⚠️ Please select at least one ticket.")
            else:
                try:
                    conn = get_db_connection()
                    with conn.cursor() as cursor:
                        print(f"Booking for Event ID: {event['id']}, User ID: {st.session_state.user_id}")

                        cursor.execute("""
                            UPDATE events 
                            SET vip_tickets = vip_tickets - %s, general_tickets = general_tickets - %s 
                            WHERE id = %s AND status = 'active'
                        """, (vip_tickets, general_tickets, event['id']))
                        
                        if cursor.rowcount == 0:
                            st.error("⚠️ Event not found, already canceled, or tickets not available!")
                            conn.rollback()
                            st.stop()

                        cursor.execute("""
                            INSERT INTO bookings (user_id, event_id, vip_tickets_booked, general_tickets_booked) 
                            VALUES (%s, %s, %s, %s)
                        """, (st.session_state.user_id, event['id'], vip_tickets, general_tickets))

                        if cursor.rowcount == 0:
                            st.error("⚠️ Booking failed. Please try again.")
                            conn.rollback()
                        else:
                            conn.commit()
                            st.success(f"✅ Successfully booked {vip_tickets} VIP and {general_tickets} General ticket(s)! Total Cost: ${total_cost:.2f}")
                            print("✅ Booking confirmed in the database!")

                except Exception as e:
                    conn.rollback()
                    st.error(f"⚠️ Error booking tickets: {str(e)}")
                    print(f"Error: {str(e)}")

                finally:
                    conn.close()

# ✅ Update Event (Only for Organizers, restricted to their own active events)
if menu == "Update Event":
    if st.session_state.role != "organizer":
        st.error("❌ Only organizers can update events.")
    else:
        st.subheader("✏️ Update Event")
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM events WHERE user_id = %s AND status = 'active'", (st.session_state.user_id,))
        events = cursor.fetchall()
    conn.close()
    
    if not events:
        st.info("📢 You have no active events to update.")
    else:
        event_options = {event['title']: event for event in events}
        selected_event = st.selectbox("Select Event to Update", list(event_options.keys()))
        event = event_options[selected_event]
        
        # Show current poster if it exists
        if event['poster_path']:
                st.write("Current Poster:")
                try:
                    st.image(event['poster_path'], use_container_width=True, width=200)
                except FileNotFoundError:
                    st.warning("⚠️ Current poster not found.")
        else:
            st.write("🖼️ No poster currently set.")    

        new_title = st.text_input("Event Title", value=event['title'])
        new_location = st.text_input("Location", value=event['location'])
        new_description = st.text_area("Description", value=event['description'])
        new_capacity = st.number_input("Total Capacity", min_value=1, value=event['capacity'])
        
        # Poster upload for update
        new_poster_file = st.file_uploader("Upload New Poster (PNG, JPG)", type=["png", "jpg", "jpeg"], key=f"poster_update_{event['id']}")
        
        if st.button("Update Event"):
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    # Initialize poster_path
                    poster_path = event['poster_path']
                    old_poster_path = poster_path  # Store for potential deletion
                    # Handle new poster upload
                    if new_poster_file:
                            import os
                            from datetime import datetime
                            # Create unique filename with timestamp to avoid conflicts
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            file_extension = os.path.splitext(new_poster_file.name)[1]
                            poster_filename = f"event_{event['id']}_{timestamp}{file_extension}"
                            poster_path = os.path.join("posters", poster_filename)
                                    
                            # Save the new poster
                            os.makedirs("posters", exist_ok=True)
                            with open(poster_path, "wb") as f:
                                f.write(new_poster_file.getbuffer())    

                    cursor.execute(
                        "UPDATE events SET title=%s, location=%s, description=%s, capacity=%s, poster_path=%s WHERE id=%s AND user_id=%s AND status = 'active'",
                        (new_title, new_location, new_description, new_capacity, poster_path, event['id'], st.session_state.user_id)
                    )
                    if cursor.rowcount == 0:
                        st.error("⚠️ No event updated. Either it doesn't exist, is canceled, or you don't have permission.")
                    else:
                        conn.commit()
                        # Delete old poster if a new one was uploaded and old one exists
                        if new_poster_file and old_poster_path and os.path.exists(old_poster_path):
                                try:
                                    os.remove(old_poster_path)
                                except Exception as e:
                                    st.warning(f"⚠️ Could not delete old poster: {str(e)}")
                        st.success("✅ Event updated successfully!")
            except Exception as e:
                st.error(f"⚠️ Error updating event: {str(e)}")
            finally:
                conn.close()

# ✅ Cancel Event (Only for Organizers, restricted to their own events)
if menu == "Cancel Event":
    if st.session_state.role != "organizer":
        st.error("❌ Only organizers can cancel events.")
    else:
        # Existing code for canceling events...
        st.subheader("❌ Cancel Event")
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM events WHERE user_id = %s AND status = 'active'", (st.session_state.user_id,))
        events = cursor.fetchall()
    conn.close()
    
    if not events:
        st.info("📢 You have no active events to cancel.")
    else:
        event_options = {event['title']: event for event in events}
        selected_event = st.selectbox("Select Event to Cancel", list(event_options.keys()))
        event = event_options[selected_event]
        
        # Check if there are bookings for this event
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as booking_count FROM bookings WHERE event_id = %s", (event['id'],))
            booking_count = cursor.fetchone()['booking_count']
        conn.close()

        st.write(f"This event has {booking_count} booking(s). Canceling it will mark it as canceled, but bookings will remain.")
        
        if st.button("Cancel Event"):
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    # Update the event status to 'canceled'
                    cursor.execute(
                        "UPDATE events SET status = 'canceled' WHERE id = %s AND user_id = %s AND status = 'active'",
                        (event['id'], st.session_state.user_id)
                    )
                    if cursor.rowcount == 0:
                        st.error("⚠️ No event canceled. Either it doesn't exist, is already canceled, or you don't have permission.")
                    else:
                        conn.commit()
                        st.success("✅ Event marked as canceled successfully!")
            except Exception as e:
                st.error(f"⚠️ Error canceling event: {str(e)}")
            finally:
                conn.close()
    

# ✅ Logout
if menu == "Logout":
    st.session_state.clear()
    st.success("✅ Logged out!")
    st.rerun()
