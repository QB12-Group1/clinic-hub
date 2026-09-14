from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# TODO: eventually support Django ORM-style nested lookups (e.g., obj1__obj2__some_field)
#       — not blocking now, we'll see how it goes with the current implementation
@register.filter
def get_item(value, key):
    """Read a dictionary key or object attribute from generic table rows."""
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


@register.filter
def ui_field(field):
    """Render a Django form field with the project's default daisyUI styling."""
    widget_type = field.field.widget.__class__.__name__.lower()
    if "checkbox" in widget_type:
        css_class = "checkbox checkbox-primary"
    elif "select" in widget_type:
        css_class = "field-control select appearance-none"
    elif "textarea" in widget_type:
        css_class = "field-control min-h-32 resize-y py-3"
    else:
        css_class = "field-control"
    if field.errors:
        css_class += " field-control-error"
    return mark_safe(field.as_widget(attrs={"class": css_class}))
