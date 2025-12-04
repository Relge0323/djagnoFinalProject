from django import template

#create a new template library instance so we can register custom filters
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """
    Custom template filter to add a CSS class to a Django form field
    
    used with username field in the login.html and signup.html files
      {{form.username|add_class:"form-control"}}

    this renders the input with the specified class
        <input type="text" name="username" class="form-control">
    """
    return field.as_widget(attrs={"class": css})
