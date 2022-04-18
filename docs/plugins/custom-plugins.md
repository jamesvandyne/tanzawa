# Custom Plugins 

As Tanzawa Plugins are regular Django applications, developing a Tanzawa Plugin has the same ergonomics as Django development.  


## Requirements

In order for your Plugin to be seen by Tanzawa, it must have:

1. A `Plugin` class that inherits from `data.plugins.plugin.Plugin`. This is the interface between Tanzawa and a plugin.
2. A `tanzawa_plugin.py` or `tanzawa_plugin` python package that instantiates the plugin and registers it with the Tanzawa Plugin Pool.  

If your application lives outside of Tanzawa itself, you must install it manually by adding the package name to the `PLUGINS` environment variable.


## Plugin Interface

Each Plugin is required to provide some base information to Tanzawa so users can understand the plugin's functionality.

### Name

The name of the plugin. This is the main identifier for the user, so try to make it as simple and self-descriptive as possible.

### Identifier

A reverse-url style unique identifier for the plugin. This is stored in the database to let Tanzawa know which plugins are active and is not shown the user.

e.g. The bundled "Now page" plugin's identifier is `blog.tanzawa.plugins.nowpage`.

### Description

Provide an easy to understand description of what your plugin provides. This should be a plain text string,
but can also be rendered HTML using Django templates if you want to provide links.

```python
from django.template.loader import render_to_string
...
    @property
    def description(self):
        return render_to_string("now/description.html")

```

### Settings URL

Each plugin can provide a single URL that acts as the user's entry point to configure the plugin. This
is the "settings" link that is displayed next to each plugin in the admin. Should return None if not configurable.

```python
from django import urls
...
    @property
    def settings_url(self):
        return urls.reverse_lazy("plugin_now_admin:update_now")
``` 

### Top Navigation

Providing top navigation requires two settings: `has_public_top_nav` and `render_navigation`.

#### has_public_top_nav

A boolean value indicating if a plugin is providing top menu items.

#### render_navigation

A function that renders the actual navigation. It has two inputs: `context` and `render_location`.

* `context` is a regular django context containing the entire context for that page.
  * `nav` contains the id of the currently selected page. Use this variable to decide if your navigation is selected and should indicate as such e.g. underlined.
* `render_location` is the name of the location that Tanzawa is rendering. This could be used to provide different layouts depending on the location. 

```python
from django import template
...

    def render_navigation(
        self,
        *,
        context: template.Context,
        render_location: str,
    ) -> str:
        """Render the public facing navigation menu item."""
        t = context.template.engine.get_template("now/navigation.html")
        return t.render(context=context)
```

Example top navigation template for desktop display.

```djangotemplate
<a href="{% url "plugin_now:now" %}" class="ml-2 leading-8 hidden md:inline-block{% if nav == "now" %} border-b-4 border-negroni-900{% endif %}">
    <span class="mr-1">👉</span>Now
</a>
```

### Feed Hooks

Allow plugins to add content before or after each entry in a feed.

#### has_feed_hooks

A boolean value indicating if a plugin is hooking into the feed content generation.


#### feed_before_content

Called for each post in a feed. Input is a single `post` object of type `data.posts.TPost`.


#### feed_after_content

Called for each post in a feed. Input is a single `post` object of type `data.posts.TPost`.

Example implementation using a template to render content.

```python
from django import template
...

    def feed_after_content(self, post: Optional[post_models.TPost] = None) -> str:
        template = loader.get_template("comment_by_email/feed.html")
        return template.render(context={"post": post})
```

## Registering Your Plugin

```python
from plugins import plugin, pool

class NowPlugin(plugin.Plugin):
    ...

def get_plugin() -> plugin.Plugin:
    return NowPlugin()

pool.plugin_pool.register_plugin(get_plugin())
```

## Admin Views

Views in the admin should be contained in `admin_urls.py`. Each view should be protected with the
Django `@login_required` decorator to ensure anonymous users cannot change settings or access sensitive data.

```python
from django.urls import path

from . import views

app_name = "plugin_now_admin"

urlpatterns = [
    path("edit/", views.UpdateNowAdmin.as_view(), name="update_now"),
]
```
The admin views will be automatically included at `/a/plugins/slugified-plugin-name/`.


## Public Views

Views that should be publicly accessible should be contained in `urls.py`. Note as plugin urls are included
 before stream urls, if your public urls match a user's stream, your plugin will take precedence. 


```python
from django.urls import path

from . import views

app_name = "plugin_now"

urlpatterns = [
    path("now/", views.PublicViewNow.as_view(), name="now"),
]

```

## Migrations
 
Tanzawa will automatically run migrations on two occasions:
 
1. When the plugin is activated.
2. When the server starts (to allow for automatic upgrades of the DB schema in the future).
 
To disable automatically migrating when starting the server, set
`PLUGINS_RUN_MIGRATIONS_STARTUP` to `False` in your `.env` file.
 
### Creating Migrations
 
 If your plugin is not enabled, first enable the plugin.
 
 ```
$ python3 apps/manage.py enable_plugin blog.tanzawa.plugins.nowpage
```

Once the plugin is enabled you can make migrations as usual.

```
$ python3 apps/manage.py makemigrations now
```
 
### Running Migrations Manually
 
After a plugin is enabled you can run migrations as if it were a regular django application.

```
$ python3 apps/manage.py migrate now
`
```  
 
 
## Templates
 
Templates are regular Django templates and should be placed in a `templates/<plugin-app-name>` directory inside of your plugin.