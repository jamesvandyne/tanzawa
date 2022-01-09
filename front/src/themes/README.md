# Themes

Each theme should put it's compiled assets in the `static` directory inside the theme's source directory.

To avoid conflicts, all assets inside static should be contained in a directory with the same name as the theme.

```
themes
├── README.md
└── platinum
    ├── static
    │   └── platinum
    │       └── style.css  # distribution
    ├── style.css  # source
    ├── tailwind.config.js
```

The main stylesheet must be called `style.css`.

### Compiling Styles

Use tailwind-cli to compile css assets.

```
$ npx tailwindcss -i ./style.css -o ./static/platinum/style.css 
```