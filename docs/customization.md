# Customization

### Environment Variables

You can adjust the values below in your `.env` to modify certain behaviors of Tanzawa. 


|Setting name|Values|Description|
|---|---|---|
|OPEN_GRAPH_USE_OPEN_GRAPH|`True`, `False`|Render OpenGraph properties in head|
|OPEN_GRAPH_USE_TWITTER|`True`, `False`|Render Twitter properties in head|
|OPEN_GRAPH_USE_FACEBOOK|`True`, `False`|Render Facebook properties in head|

### Site Settings

1. Visit the Django Settings by visiting `/admin/` or opening the Tanzawa Dashboard and clicking `Settings`.
2. Click the "Site Settings" and add a record.

From the Site Settings screen you can set:

1. Site title
2. Site subtitle
3. Site emoji
4. Active Theme
5. Footer HTML content 


### Add Streams / Modifying the Navigation

Streams are how you categorize posts in Tanzawa. By default Tanzawa creates streams to covert most basic IndieWeb content types.

1. Open the Django Settings in your browser  `/admin/`
2. Click add stream and fill in the form as you wish.
   1. Icon: Input an emoji of your choice.
   2. Name: This will appear on the left as navigation.
   3. Slug: Generally this is the name in lowercase and will appear in stream urls e.g. `example.com/notes`
