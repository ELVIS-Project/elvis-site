# LM: TODO lots of cleaning up
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer, JSONPRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from django.template import RequestContext
from django.shortcuts import render_to_response
from elvis import celery
import os


from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.download import DownloadSerializer, DownloadingSerializer
from elvis.models.download import Download
from elvis.models.piece import Piece
from elvis.models.movement import Movement

from django.core.exceptions import ObjectDoesNotExist

class DownloadListHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_list.html"


class DownloadDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download.html"

class DownloadingHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/downloading.html"

class DownloadList(generics.ListCreateAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadListHTMLRenderer)

    def get_queryset(self):
        user = self.request.user
        return Download.objects.filter(user=user)


class DownloadDetail(generics.RetrieveUpdateAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadDetailHTMLRenderer)

    def get_object(self):
        user = self.request.user
        
        try:
            obj = Download.objects.filter(user=user).latest("created")
            return obj
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # print("I AM BEING PATCHED");
        itype = request.DATA.get("type", None)
        item_id = request.DATA.get('item_id', None)

        if itype not in ('piece', 'movement'):
            return Response({'message': "You must supply either piece or movement"}, status=status.HTTP_400_BAD_REQUEST)

        if itype == 'piece':
            obj = Piece.objects.get(pk=item_id)
        elif itype == 'movement':
            obj = Movement.objects.get(pk=item_id)

        if not obj:
            return Response({'message': "The item with id {0} was not found".format(item_id)}, status=status.HTTP_404_NOT_FOUND)
       
        dlobj = self.get_object()
        
        for attachment in obj.attachments.all():
            dlobj.attachments.add(attachment)

        d = DownloadSerializer(dlobj).data
        return Response(d)

        # return self.partial_update(request, *args, **kwargs)

# LM: Original preliminary view for downloading, will probably be removed
class Downloading(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadingSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadingHTMLRenderer)


# LM: New view for downloading files
@csrf_protect#require_http_methods(["POST"])
def downloading_item(request):
    c = {}

    #print(request)

    # LM: Things needed:
    # 1. Parse request to extract path to all requested files
    # 2. Create subprocess - Celery
    # 3. Get files and copy into dummy directory
    # 4. Zip directory
    # 5. Track subprocess
    # 6. Serve
    # 7. Remove dummy directory and zipped file
    # 

    items = request.POST.getlist('item')
    print('items', items)

    types = request.POST.getlist('extension')
    print('types', types)

    others_check = False
    extensions = types
    if 'midi' in types:
        extensions.append('mid')
    if 'xml' in types:
        extensions.append('mxl')
    if 'OTHERS' in types:
        others_check = True

    print('extensions', extensions)


    # If user checks all exts except .abc, he would expect everything else but .abc
    # -> need a list of everything that could have been left unchecked
    # EDIT IF download.html IS CHANGED
    default_exts = ['mei', 'xml', 'midi', 'pdf', 'krn', 'mid', 'mxl']

    print('default_exts', default_exts)

    # Check for two conditions. Either:
    # 1) requested file is in selected extensions
    # 2) file is not in available extensions (i.e. its extension was not rejected) and OTHERS was checked
    files = []
    for item in items:
        fileName, fileExt = os.path.splitext(item)
        if (fileExt in extensions or fileExt in extensions):
            files.append(item)
        elif((not (fileExt in default_exts or fileExt in default_exts)) and others_check):
            files.append(item)
        else:
            pass

    print('files', files)

    print('user', request.user.username)

    
    celery.zip_files(files, request.user.username)

    #c.update(csrf(request))
    return render_to_response("download.html", RequestContext(request, {}))



