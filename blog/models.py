from django.db import models
from django import forms

# Add these:
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel

from wagtail.search import index
from wagtail.snippets.models import register_snippet


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
# add the get_context method:
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
     # Add this:
    authors = ParentalManyToManyField('blog.Author', blank=True)
# Add the main_image method:
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]
        

    class BlogPageGalleryImage(Orderable):
        page = ParentalKey(Page, on_delete=models.CASCADE, related_name='gallery_images')
        image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
        caption = models.CharField(blank=True, max_length=250)

        panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
        
    @register_snippet
    class Author(models.Model):
        name = models.CharField(max_length=255)
        author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

        panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

  #  def __str__(self): return self.name  (it was giving attribute erro)

    class Meta:
        verbose_name_plural = 'Authors'
        
