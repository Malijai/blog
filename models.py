# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.db.models import permalink
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField
from django.db import models
#from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
class Tag(models.Model):
   mot_en = models.CharField(max_length=100, unique=True, error_messages={'unique':_("Ce mot clef existe déjà")})
   slug = models.SlugField(max_length=100)

   class Meta:
       ordering = ['mot_en']

   def __str__(self):
       return '%s' % self.mot_en


#   @permalink
#   def get_absolute_url(self):
#       return ('view_blog_tag', None, {'slug': self.slug})

class Entree(models.Model):
    titre_en = models.CharField(max_length=200)
    texte_en = RichTextField(config_name='billet')
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    posted = models.DateTimeField(db_index=True, auto_now_add=True)
    tag = models.ManyToManyField(Tag)
    #    groupe = models.ForeignKey(Group, blank=True, null=True, on_delete=models.DO_NOTHING, help_text=_("optionnel: définir un groupe pour limiter l'envoi de courriel à ses membres"), limit_choices_to=~models.Q(name__in=['SansCourriel']))

    class Meta:
       ordering = ['-posted']

    def __str__(self):
        return '%s' % self.titre_en


class Commentaire(models.Model):
    texte_en = RichTextField(config_name='comment')
    entree = models.ForeignKey(Entree, on_delete=models.DO_NOTHING)
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    posted = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ['posted']

    def __str__(self):
        return  '%s' % self.texte_en


    


