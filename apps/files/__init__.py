import mimetypes

# macOS mimetypes recognizes webp while linux does not. Remove once linux supports it (3.9.2 ?)
mimetypes.add_type('image/webp', '.web')