from django.shortcuts import render
from models import Attachment
from django.http import HttpResponseRedirect
from django.core.files import File
from django import forms
from .forms import AttachmentForm
from .custom_storage import CustomStorage

def index(request):
    attachment_list = Attachment.objects.order_by('-upload_date')
    context = {'attachment_list': attachment_list}
    return render(request, 'object_storage/index.html', context)

def uploaded(request):
	cs = CustomStorage()
	if request.method == 'POST':
		form = AttachmentForm(request.POST, request.FILES)

		#if form.is_valid():
		name = request.POST['name']
		#else:
		#	name = 'newname'
		mimetype = request.FILES['attachment'].content_type
		attachment = request.FILES['attachment'].read()
		uploaded_date = form.fields['uploaded_date']

	else:
		form = AttachmentForm()

	context = {'form': form}

	response = cs._save(name, attachment, mimetype)
	context.update({'status': response.status_code, 'text': response.text })

	return render(request, 'object_storage/uploaded.html', context)

def upload_form(request):
	form = AttachmentForm()
	context = {'form': form}
	return render(request, 'object_storage/upload_form.html', context)

def uploaded_form(request):
	cs = CustomStorage()

	if request.method == 'POST':
		form = AttachmentForm(request.POST, request.FILES)

		if form.is_valid():
			name = form.cleaned_data['name']
			mimetype = form.cleaned_data['attachment'].content_type
			attachment = form.cleaned_data['attachment'].read()
			uploaded_date = form.cleaned_data['uploaded_date']

		else:
			name = "form not valid"

	else:
		form = AttachmentForm()

	context = {'form': form}

	response = cs._save(name, attachment, mimetype)
	context.update({'status': response.status_code, 'text': response.text })

	return render(request, 'object_storage/uploaded.html', context)