from django.shortcuts import render


def dashboard(request):
    context = {
        "stats": [
            {
                "label": "Appointments today",
                "value": "24",
                "change": "+8.2%",
                "icon": "calendar-check-2",
                "tone": "primary",
            },
            {
                "label": "Active patients",
                "value": "1,284",
                "change": "+12.5%",
                "icon": "users",
                "tone": "secondary",
            },
            {
                "label": "Revenue this month",
                "value": "$18.6k",
                "change": "+6.4%",
                "icon": "wallet-cards",
                "tone": "accent",
            },
            {
                "label": "Avg. satisfaction",
                "value": "4.9",
                "change": "+0.3",
                "icon": "star",
                "tone": "violet-500",
            },
        ],
        "appointments": [
            {
                "time": "09:00",
                "patient": "Mina Rahimi",
                "type": "Follow-up",
                "doctor": "Dr. Arman Sadeghi",
                "status": "Confirmed",
                "status_tone": "success",
                "tone": "primary",
            },
            {
                "time": "10:30",
                "patient": "Reza Moradi",
                "type": "Initial consultation",
                "doctor": "Dr. Niloofar Kamali",
                "status": "Checked in",
                "status_tone": "info",
                "tone": "secondary",
            },
            {
                "time": "13:00",
                "patient": "Sara Ahmadi",
                "type": "Routine checkup",
                "doctor": "Dr. Arman Sadeghi",
                "status": "Confirmed",
                "status_tone": "success",
                "tone": "accent",
            },
            {
                "time": "15:30",
                "patient": "Omid Karimi",
                "type": "Lab results",
                "doctor": "Dr. Niloofar Kamali",
                "status": "Pending",
                "status_tone": "warning",
                "tone": "secondary",
            },
        ],
        "bars": [
            {"day": "Mon", "height": 75, "fill": 68},
            {"day": "Tue", "height": 90, "fill": 82},
            {"day": "Wed", "height": 65, "fill": 54},
            {"day": "Thu", "height": 100, "fill": 88},
            {"day": "Fri", "height": 80, "fill": 72},
            {"day": "Sat", "height": 48, "fill": 38},
            {"day": "Sun", "height": 30, "fill": 22},
        ],
        "doctors": [
            {
                "name": "Dr. Arman Sadeghi",
                "specialty": "Cardiology",
                "initials": "AS",
                "tone": "primary",
            },
            {
                "name": "Dr. Niloofar Kamali",
                "specialty": "Family medicine",
                "initials": "NK",
                "tone": "secondary",
            },
            {
                "name": "Dr. Pouya Etemadi",
                "specialty": "Dermatology",
                "initials": "PE",
                "tone": "accent",
            },
        ],
    }
    return render(request, "dashboard.html", context)
