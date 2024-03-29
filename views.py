# -*- coding: utf-8 -*-
#from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from .forms import CommentaireForm, EntreeForm, TagForm, RechercheForm
from .models import Entree, Tag
from accueil.models import Projet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import slugify
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class BlogDetail(generic.DetailView):
    template_name = 'blogdetail.html'
    model = Entree


def ismanitoba(http_host):
    return True if 'ntpmb.ca' in http_host else False
    #   return True


def ismalijai(http_host):
    return True if 'malijai.org' in http_host else False
    #   return True


def isntp(http_host):
    return True if 'ntp-ptn.org' in http_host else False
    #   return True


@login_required(login_url=settings.LOGIN_URI)
def listing(request):
    post_list = Entree.objects.all()
    paginator = Paginator(post_list, 5)
    #  Show 5 post par page
    tag_list = Tag.objects.all()
    #  Utilisé pour la liste de tous les mots clefs avec un lien
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #   If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        #   If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'list.html', {'posts': posts, 'tags': tag_list})


def fait_courriel_commentaire(commentaire, posttitre, billetacommenter, host):
    lienpost = posttitre + ' (' + settings.BLOG_URL + str(billetacommenter.id) + ' )'
    if host == 'MB':
        sujet = _(u"Nouveau commentaire dans le blog de NTP Manitoba")
        textecourriel = _(u"""
        Un nouveau commentaire au billet intitulé : {} vient d'être publié par {} {}.
        Vous recevez ce courriel parce que vous ête membre de l'équipe du projet NTP Manitoba.
        Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.

        Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
            """).format(lienpost, commentaire.author.first_name, commentaire.author.last_name)
    elif host == 'NTP2':
        sujet = _(u"Nouveau commentaire dans le blog de NTP2 Community")
        textecourriel = _(u"""
        Un nouveau commentaire au billet intitulé : {} vient d'être publié par {} {}.
        Vous recevez ce courriel parce que vous ête membre de l'équipe du projet NTP2 Community.
        Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.

        Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
            """).format(lienpost, commentaire.author.first_name, commentaire.author.last_name)
    else:
        sujet = _(u"Nouveau commentaire dans le blog de l'observatoire")
        textecourriel = _(u"""
    Un nouveau commentaire au billet intitulé : {} vient d'être publié par {} {}.
    Vous recevez ce courriel parce que vous ête membre de l'Observatoire en santé mentale et justice du Québec.
    Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.
    Merci de participer à ce projet.

    Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
        """).format(lienpost, commentaire.author.first_name, commentaire.author.last_name)
    return sujet, textecourriel


def fait_courriel_entree(entree, host):
    lienpost = entree.titre_en + ' (' + settings.BLOG_URL + str(entree.id) + ' )'
    if host == 'MB':
        sujet = _(u"Nouveau billet dans le blog de NTP Manitoba")
        textecourriel = _(u"""
    Un nouveau billet intitulé : {} vient d'être publié par {} {}.
    Vous recevez ce courriel parce que vous ête membre du projet NTP Manitoba.
    Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.

    Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
    """).format(lienpost, entree.author.first_name, entree.author.last_name)
    elif host == 'NTP2':
        sujet = _(u"Nouveau billet dans le blog de NTP2 Community")
        textecourriel = _(u"""
    Un nouveau billet intitulé : {} vient d'être publié par {} {}.
    Vous recevez ce courriel parce que vous ête membre du projet NTP2 Community.
    Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.

    Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
    """).format(lienpost, entree.author.first_name, entree.author.last_name)
    else:
        sujet = _(u"Nouveau billet dans le blog de l'observatoire")
        textecourriel = _(u"""
        Un nouveau billet intitulé : {} vient d'être publié par {} {}.
        Vous recevez ce courriel parce que vous ête membre de l'Observatoire en santé mentale et justice du Québec.
        Ne répondez pas à ce courriel, il s'agit d'un envoi automatisé.
        Merci de participer à ce projet.

        Malijaï Caulet (malijai.caulet.ippm@ssss.gouv.qc.ca)
        """).format(lienpost, entree.author.first_name, entree.author.last_name)
    return sujet, textecourriel


@login_required(login_url=settings.LOGIN_URI)
def commentaire_new(request, pk):
    billetacommenter = Entree.objects.get(pk=pk)
    posttitre = billetacommenter.titre_en
    if request.method == "POST":
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.entree = Entree.objects.get(pk=pk)
            commentaire.author = request.user
            commentaire.save()
            if ismanitoba(request.META.get('HTTP_HOST')):
                sujet, textecourriel = fait_courriel_commentaire(commentaire, posttitre, billetacommenter, 'MB')
            elif isntp(request.META.get('HTTP_HOST')):
                sujet, textecourriel = fait_courriel_commentaire(commentaire, posttitre, billetacommenter, 'NTP2')
            else:
                sujet, textecourriel = fait_courriel_commentaire(commentaire, posttitre, billetacommenter, '')
            envoi_courriel(sujet, textecourriel)
            return redirect('blogdetail', pk=pk)
    else:
        form = CommentaireForm()
    return render(request, "commentaire_edit.html", {'form': form, 'post_id': pk, 'Posttitre':  posttitre})


def envoi_courriel(sujet, textecourriel):
    users_ntp2 = [p.user for p in Projet.objects.filter(Q(projet=Projet.NTP2) | Q(projet=Projet.ALL))]
    courriels = [user.email for user in users_ntp2 if user.email and user.is_active]
    with mail.get_connection() as connection:
        mail.EmailMessage(
            sujet, textecourriel, 'malijai.caulet@ntp-ptn.org', courriels,
            connection=connection,
        ).send()


@login_required(login_url=settings.LOGIN_URI)
def entree_new(request):
    tag_list = Tag.objects.all()
    #    group_list = Group.objects.exclude(name=u'SansCourriel')
    if request.method == "POST":
        form = EntreeForm(request.POST)
        if form.is_valid():
            entree = form.save(commit=False)
            entree.author = request.user
            entree.save()
            form.save_m2m()
            #  form save many to many (ici les tags selectionnes)
            #  import ipdb; ipdb.set_trace()
            if ismanitoba(request.META.get('HTTP_HOST')):
                sujet, textecourriel = fait_courriel_entree(entree, 'MB')
                envoi_courriel(sujet, textecourriel)
            elif isntp(request.META.get('HTTP_HOST')):
                sujet, textecourriel = fait_courriel_entree(entree, 'NTP2')
                envoi_courriel(sujet, textecourriel)
            else:
                sujet, textecourriel = fait_courriel_entree(entree, '')
                envoi_courriel(sujet, textecourriel)
            return redirect('blogdetail', entree.id)
    else:
        form = EntreeForm()
        #  return render(request, "entree_edit.html", {'form': form, 'tags':tag_list, 'groupes':group_list,})
    return render(request, "entree_edit.html", {'form': form, 'tags': tag_list})


@login_required(login_url=settings.LOGIN_URI)
def tag_new(request):
    tag_list = Tag.objects.all()
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.slug = slugify(tag.mot_en)
            tag.save()
            return redirect('entree_new')
    else:
        form = TagForm()
    return render(request, "tag_edit.html", {'form': form, 'tags': tag_list})


@login_required(login_url=settings.LOGIN_URI)
def view_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    return render(request, 'view_tag.html', {
        'tag': tag,
        'entrees': Entree.objects.filter(tag=tag)  # [:10]
    })


@login_required(login_url=settings.LOGIN_URI)
def get_recherchetexte(request):
    form_class = RechercheForm
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            texte = request.POST.get('recherchetexte', '')
            post_list = Entree.objects.filter(texte_en__icontains=texte)
            if post_list:
                tag_list = Tag.objects.all()
                return render(request, 'list.html', {'posts': post_list, 'tags': tag_list})
            else:
                return render(request, 'recherche.html', {'form': form_class, 'message': texte})
    else:
        form_class = RechercheForm()

    return render(request, 'recherche.html', {'form': form_class})


def index(request):
    return render(request, 'logout.html')
