# Generate Image

生成图片

注册名：`generate_image`

接受参数:
``` json
{
  "model_id": null, // Unique identifier used to locate and load the target model, if not specified, the model will be selected based on the user's preferences.
  "brief_summary": "", // The alternate text used after the image is generated.
  "prompt": "", // The prompt to generate an image.
  "images": null // The images to use as a reference for the generation.
}
```

返回生成后的图片链接：
``` json
{
  "images": [], // The generated images.
  "markdown_images": [] // The generated images as markdown.
}
```