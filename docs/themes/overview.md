# Overview
Themes allow you to customize the color scheme used by your website.

## Theme location

Themes live in `front/src/themes/`.  Each theme must be contained in its own directory. 

Distribution files must be in `front/src/themes/<themename>/static/<themename>/`.

The distribution stylesheet must be named `style.css` and be at the root of the static directory i.e. `front/src/themes/<themename>/static/<themename>/style.css`

## How to create a theme

Create a `tailwind.config.js` in your new theme directory. 


To generate the appropriate styles, set the `content` value of your tailwind config as follows:

```
  content: [
    './../../../../apps/templates/base_public.html',
    './../../../../apps/templates/registration/login.html',
    '../../../../apps/templates/public/**/*.html',
    '../../../../src/public_controllers/*.js',
  ]
```

Setup your theme and define the following colors:

```
  theme: {
    colors: {
      'white': '#ffffff',
      'black': '#000000',
      'transparent': 'transparent',
      'current': 'currentColor',
      'primary': {
        DEFAULT: '#dddddd',  // main background color
        '600': '#CCCCCC',  // button color
        '800': '#BFBFBF', // button border color
      },
      'secondary': {
        DEFAULT: '#999CFC',  // selection underline / site name color 
        '600': '#97948f',  // footer/line between posts
        '800': '#7476d6',  
        '900': '#1a1c64',
      },
      },
    extend: {
      spacing: {
        '99': '45rem',
      },
    },
    variants: {
      extend: {},
    },
  },
```

Inside your style.css, in addition to the tailwind base classes, define the following classes:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;


.selected {
  @apply border-r-4  border-secondary;
}

.primary-button {
    @apply rounded bg-primary-600 border-primary-800 px-3 py-1 border;
}
```

## Building your theme

Tanzawa themes require Tailwind 3.0. From your theme's root directory, run the following command to build your theme.

```
$ npx tailwindcss -i ./style.css -o ./static/<themename>/style.css
```

Add `--watch` at the end of the command during development of your theme to automatically recompile the theme as you make changes to the css.

 
## Activating your theme

Activate your theme in the Django admin by visiting `admin/settings/msitesettings/1/change/`, selecting your theme from the dropdown, and saving.
 
Note in production usages of Tanzawa, you must start the django server and run `manage.py collectstatic` management command after uploading your theme to allow access to the new theme assets and styles.