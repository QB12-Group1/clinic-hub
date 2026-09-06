# Clinic Hub frontend cheatsheet

You do not need to be a frontend developer to reuse this UI. Django templates are the main building blocks; each component is a normal HTML fragment that receives a small dictionary of values.

## Reuse a component

```django
{% include "components/stat_card.html" with stat=stat %}
{% include "components/doctor_card.html" with doctor=doctor %}
{% include "components/appointment_row.html" with item=appointment %}
```

The expected fields are visible in the matching file under `templates/components/`.

## Add a new page

```django
{% extends "base.html" %}
{% block title %}Patients · Clinic Hub{% endblock %}
{% block content %}
<main class="mx-auto max-w-6xl p-6">
  <div class="surface p-6"><h1 class="text-2xl font-extrabold">Patients</h1></div>
</main>
{% endblock %}
```

Useful shared classes:

- `surface`: white rounded card with border and soft shadow
- `eyebrow`: small uppercase section label
- daisyUI: `btn`, `badge`, `select`, `avatar`, `alert`, `modal`, `table`

## HTMX pattern

Keep the full page and the replaceable fragment separate:

```django
<button class="btn btn-primary" hx-get="{% url 'appointments:today' %}"
        hx-target="#appointment-list" hx-swap="outerHTML">Refresh</button>
{% include "partials/appointment_list.html" %}
```

Your Django view returns the same partial for HTMX requests. The browser swaps only `#appointment-list`; no custom JavaScript is needed.

## Alpine pattern

Use Alpine for small browser-only state such as menus, tabs, and modals:

```html
<div x-data="{ open: false }">
  <button class="btn" @click="open = !open">Toggle</button>
  <div x-show="open" x-transition>Content</div>
</div>
```

## Icons

Use any lucide icon name as an attribute:

```html
<i data-lucide="calendar-days" class="size-5"></i>
```

Icons are automatically converted after the page loads and after HTMX swaps.

## Toast notifications

Use Django messages anywhere in a view:

```python
from django.contrib import messages

messages.success(request, "Patient created successfully.")
messages.error(request, "We could not save that appointment.")
messages.warning(request, "This doctor is almost fully booked.")
messages.info(request, "Your export is being prepared.")
```

The base template automatically renders these as polished, dismissible toasts. They disappear after five seconds and include a visual progress bar. You do not need to add toast markup to individual pages.

## Recommended project structure

```text
templates/
  base.html
  components/       # small reusable visual pieces
  partials/         # HTMX replaceable sections
  pages/            # complete screens
```

Keep business logic in Django views/forms/models. Keep components presentational: pass them prepared values and let the template render them.

## Generic CRUD page foundations

The starter includes model-agnostic page templates under `templates/pages/`:

- `pages/list.html`: filters, responsive table, empty state, pagination, and View/Edit links
- `pages/form.html`: Django form rendering, validation errors, CSRF, cancel/save actions
- `pages/detail.html`: read-only field grid with Back/Edit actions

Example list context:

```python
{
    "page_title": "Patients",
    "eyebrow": "Directory",
    "page_description": "Everyone currently registered at the clinic.",
    "primary_action": {"label": "Add patient", "url": "/patients/new/"},
    "columns": [
        {"label": "Name", "key": "name"},
        {"label": "Phone", "key": "phone"},
        {"label": "Status", "key": "status"},
    ],
    "rows": patients,
    "filters": [{"label": "Search", "name": "q", "placeholder": "Name or phone"}],
}
```

Each row should provide `detail_url` and `edit_url`. For a real Django `QuerySet`, either add those properties to a small view-model or prepare dictionaries in the view.

Example form view:

```python
return render(
    request,
    "pages/form.html",
    {
        "page_title": "Add patient",
        "eyebrow": "Patients",
        "form": PatientForm(request.POST or None),
        "submit_label": "Create patient",
        "cancel_url": "/patients/",
    },
)
```

Use `partials/` for fragments returned by HTMX. A list can be split into `partials/patient_table.html`, then targeted with `hx-target="#patient-table"` after filtering, deleting, or changing status.
