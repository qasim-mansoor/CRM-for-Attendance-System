from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import calendar

# def days_in_month():

#     return calendar.monthrange(dt.year, dt.month)[1]

# Create your models here.
class Customer(models.Model):
    # created_at = models.DateTimeField(auto_now_add=True)
    admission_date = models.DateTimeField(auto_now_add=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    cnic = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    emergency_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True)
    voucher_number = models.CharField(max_length=255, blank=True, null=True)
    monthly_fee = models.CharField(max_length=255, blank=True, null=True)
    assigned_trainer = models.CharField(max_length=255, blank=True, null=True)
    special_training_fee = models.CharField(max_length=255, blank=True, null=True)
    last_paid = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)

    PACKAGE_CHOICES = [
        ("Staff Member", "Staff Member"),
        ("Deans Employee", "Deans Employee"),
        ("Resident", "Resident"),
        ("General", "General"),
        ("Student", "Student"),
        ("Other", "Other"),
    ]
    package = models.CharField(max_length=30, blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return(f"{self.customer_name}")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_last_paid = getattr(self, 'last_paid', None)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._original_last_paid = instance.last_paid
        return instance
    
    def save(self, extend=0, renew=0, *args, **kwargs):
        extend = int(extend)
        renew = int(renew)
        if self._original_last_paid != self.last_paid or self.due_date == None:
            self.due_date = timezone.now() + timedelta(days=(renew)+extend)
            self._original_last_paid = self.last_paid

        if extend > 0:
            self.due_date = self.due_date + timedelta(days=extend)
        
        # # Calculate due date based on last_paid
        # self.due_date = timezone.now() + timedelta(days=(31+extend))  # Add 31 days for next month
        # # Adjust for edge cases where the next month has less than 31 days
        # if self.due_date.month == timezone.now().month:
        #     # If calculated date falls in the same month, add another month
        super().save(*args, **kwargs)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import cv2
import os
import face_recognition
import datetime
import pickle
from .models import Customer
from .forms import AddRecordForm
from .livefeed import VideoCamera
from datetime import timedelta

def custom_404(request, exception):
    return render(request, '404.html', status=404)

# Create your views here.
def home(request):
    records = Customer.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if(user is not None):
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect('home')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('home')
    else:
        # active = [True if x.last_paid < timezone.now() - datetime.timedelta(days=31) else False for x in records]
        # print(active)
        # records_info = zip(records, active)
        # return render(request, 'home.html', {'records':records, "active":active, 'records_info':records_info})
        if request.user.is_authenticated:
            # logout(request)
            return redirect("all_records")
        else:
            # logout(request)
            return render(request, "home.html")
            # return render(request, "home.html")

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def all_records(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filter = request.POST.get("filter")
            # print(f"The filter is {filter}")
            if filter.isnumeric():
                # records = Customer.objects.filter(id=filter)
                p = Paginator(Customer.objects.filter(id=filter).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            else:
                # records = Customer.objects.filter(Q(customer_name__icontains=filter))
                p = Paginator(Customer.objects.filter(Q(customer_name__icontains=filter)).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            post = True
        else:
            # records = Customer.objects.all()
            p = Paginator(Customer.objects.all().order_by('-id'), 20)
            page = request.GET.get('page')
            records = p.get_page(page)
            post = False

        # active = [True if x.last_paid < timezone.now() - datetime.timedelta(days=31) else False for x in records]
        # print(active)
        # records_info = zip(records, active)
        now = timezone.now()
        return render(request, 'all_records.html', {'records':records, 'records':records, 'post':post, 'now':now})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def active_records(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filter = request.POST.get("filter")
            if filter.isnumeric():
                # records = Customer.objects.filter(id=filter)
                p = Paginator(Customer.objects.filter(due_date__gt=timezone.now()).filter(id=filter).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            else:
                # records = Customer.objects.filter(Q(customer_name__icontains=filter))
                p = Paginator(Customer.objects.filter(due_date__gt=timezone.now()).filter(Q(customer_name__icontains=filter)).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            post = True
        else:
            # records = Customer.objects.all()
            p = Paginator(Customer.objects.filter(due_date__gt=timezone.now()).order_by('-id'), 20)
            page = request.GET.get('page')
            records = p.get_page(page)
            post = False

        # records = Customer.objects.all()
        now = timezone.now()
        return render(request, 'active_records.html', {'records':records, 'records':records, 'post':post, 'now': now})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def inactive_records(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filter = request.POST.get("filter")
            if filter.isnumeric():
                # records = Customer.objects.filter(id=filter)
                p = Paginator(Customer.objects.filter(due_date__lt=timezone.now()).filter(id=filter).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            else:
                # records = Customer.objects.filter(Q(customer_name__icontains=filter))
                p = Paginator(Customer.objects.filter(due_date__lt=timezone.now()).filter(Q(customer_name__icontains=filter)).order_by('-id'), 20)
                page = request.GET.get('page')
                records = p.get_page(page)
            post = True
        else:
            # records = Customer.objects.all()
            p = Paginator(Customer.objects.filter(due_date__lt=timezone.now()).order_by('-id'), 20)
            page = request.GET.get('page')
            records = p.get_page(page)
            post = False

        # records = Customer.objects.all()
        now = timezone.now()
        return render(request, 'inactive_records.html', {'records':records, 'records':records, 'post':post, 'now': now})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_record = get_object_or_404(Customer, id=pk)
        if request.method == "POST":
            extendby = request.POST.get("extend")
            # print(extendby)
            # customer_record.due_date += timedelta(days=int(extendby)) 
            customer_record.save(extend=int(extendby))
            return redirect('record', pk)
        # customer_record = Customer.objects.get(id=pk)
        template_name = './db2/' + str(pk)
        if not os.path.isdir(template_name):
            os.mkdir(template_name)
        images = os.listdir(template_name)
        # print(images)
        images_with_path = list(map(lambda x: str(pk) + '/' + x, images))
        # print(images_with_path)
        return render(request, 'record.html', {'customer_record': customer_record, "images": images_with_path})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    
def delete_record(request, pk):
    if request.user.is_authenticated:
        # delete_it = Customer.objects.get(id=pk)
        delete_it = get_object_or_404(Customer, id=pk)
        delete_it.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('home')
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    
def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                print(form['membership_days'].value())
                add_record = form.save()
                add_record.save(renew=form['membership_days'].value())
                print(type(add_record))
                messages.success(request, "Member Added.")
                return redirect("home")
        return render(request, 'add_record.html', {"form": form})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    
def update_record(request, pk):
    if request.user.is_authenticated:
        # current_record = Customer.objects.get(id=pk)
        current_record = get_object_or_404(Customer, id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record has been updated.")
            return redirect("home")
        return render(request, 'update_record.html', {"form": form})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def update_last_paid(request, pk):
    if request.user.is_authenticated:
        # current_record = Customer.objects.get(id=pk)
        current_record = get_object_or_404(Customer, id=pk)
        current_record.last_paid = datetime.datetime.now()
        # current_record.last_paid = datetime.datetime.now() - datetime.timedelta(days=32)
        current_record.save()
        # form = AddRecordForm(request.POST or None, instance=current_record)
        # if form.is_valid():
        #     form.save()
        #     messages.success(request, "Record has been updated.")
        #     return redirect("home")
        # return render(request, 'update_record.html', {"form": form})
        return redirect('record', pk)
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    
def detect_single_face(frame):

    rgb_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # Convert frame to RGB format
    face_locations = face_recognition.face_locations(rgb_frame)

    return len(face_locations) == 1

def capture_image(request):
    # Initialize the camera
    # cap = cv2.VideoCapture("rtsp://admin:vaival123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1")
    cap = cv2.VideoCapture(0)
    # Check if the camera opened successfully
    if not cap.isOpened():
        messages.error(request, "Error: Could not open camera.")
        return None

    # Capture a single frame
    ret, frame = cap.read()

    if not ret:
        messages.error(request, "Error: Could not capture frame.")
        cap.release()
        return None
    
    if not detect_single_face(frame):
        messages.error(request, "Either a face could not be detected or more than 1 face was detected. Make sure the person is centered in the frame with an empty background.")
        cap.release()
        return None

    # Save the captured frame as an image
    # cv2.imwrite(file_path, frame)

    # Release the camera
    cap.release()

    # messages.success(request, f"Image captured and saved as {file_path}")
    return frame

def take_pictures(request, pk):
    if request.user.is_authenticated:
        # current_record = Customer.objects.get(id=pk)
        current_record = get_object_or_404(Customer, id=pk)
        template_name = './db2/' + str(pk)
        temp_template = './temp'
        # print(template_name)

        if not os.path.isdir(template_name):
            os.mkdir(template_name)

        # print(len(os.listdir(template_name)))
            
        # cv2.imwrite(f'{template_name}/{current_record.customer_name}{len(os.listdir(template_name)) + 1}.jpg', frame)

        
        frame = capture_image(request)
        # print(frame)

        if frame is None:
            return redirect("camera", pk)
        else:
            cv2.imwrite(f'{temp_template}/temp{len(os.listdir(temp_template)) + 1}.jpg', frame)
            return redirect("confirm_save", pk)
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    
def confirm_save_pictures(request, pk):
    if request.user.is_authenticated:
        img_path = f"temp{len(os.listdir('./temp'))}.jpg"
        return render(request, "confirm_save_pictures.html", {"img": img_path, "pk": pk})

    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def update_encodings(image_path:str):
    """
    Updates a dictionary of face encodings with new encodings from an image and creates a backup before overwriting the pkl file.

    Args:
        image_path: The path to the image file.

    Returns:
        None
    """
    print(image_path)
    # Check if encodings.pkl exists
    # if os.path.exists("encodings.pkl"):
    #     # Create a backup with current timestamp
    #     timestamp = os.path.getmtime("encodings.pkl")
    #     backup_path = f"encodings_backup_{timestamp}.pkl"
    #     os.rename("encodings.pkl", backup_path)
    #     print(f"Created backup of encodings.pkl: {backup_path}")

    try:
    # Load existing encodings
        print("Encodings found")
        with open("encodings.pkl", "rb") as f:
            known_encodings = pickle.load(f)

    except FileNotFoundError:
        print("Encodings not found")
        # If file doesn't exist, create an empty dictionary
        known_encodings = {}

    # Load the image
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_encodings[image_path.split('/')[-1].split('.')[0]] = encoding

    # Save the updated dictionary
    with open("encodings.pkl", "wb") as f:
        pickle.dump(known_encodings, f)

    print(f"Updated encodings.pkl with new encodings.")


    # # Example usage
    # image_path = "path/to/your/image.jpg"
    # update_encodings(image_path)

def save_pictures(request, pk):
    
    if request.user.is_authenticated:
        current_record = get_object_or_404(Customer, id=pk)
        template_name = './db2/' + str(pk)
        temp_template = './temp'
        img = cv2.imread(f'{temp_template}/temp{len(os.listdir(temp_template))}.jpg')
        cv2.imwrite(f'{template_name}/{pk} {len(os.listdir(template_name)) + 1}.jpg', img)
        messages.success(request, f'Image saved on {template_name}/{pk} {len(os.listdir(template_name))}.jpg')
        update_encodings(f"{template_name}/{pk} {len(os.listdir(template_name))}.jpg")
        return redirect("record", pk)
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')
    

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@gzip.gzip_page
def live(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'home.html')

async def test(request):
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")

    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()

    cv2.destroyAllWindows()

def camera(request, pk):
    if request.user.is_authenticated:
        # current_record = Customer.objects.get(id=pk)
        current_record = get_object_or_404(Customer, id=pk)
        return render(request, "camera.html", {"current_record" : current_record})


    
        
from django import forms
from .models import Customer
from django.utils import timezone
import calendar

class AddRecordForm(forms.ModelForm):
    customer_name = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Customer Name", "class":"form-control"}), label="")
    father_name = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"placeholder":"Father Name", "class":"form-control"}), label="")
    nationality = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"placeholder":"Nationality", "class":"form-control"}), label="")
    cnic = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"placeholder":"CNIC/Passport Number", "class":"form-control"}), label="")
    phone_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Phone Number", "class":"form-control"}), label="")
    emergency_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Emergency Number", "class":"form-control"}), label="")
    address = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Address", "class":"form-control"}), label="")
    relationship = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Relationship", "class":"form-control"}), label="")
    voucher_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Voucher Number", "class":"form-control"}), label="")
    monthly_fee = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Monthly Fee", "class":"form-control"}), label="")
    assigned_trainer = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Assigned Trainer", "class":"form-control"}), label="")
    special_training_fee = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Special Training Fee", "class":"form-control"}), label="")
    package = forms.CharField(label="", widget=forms.Select(choices=Customer.PACKAGE_CHOICES, attrs={"class":"form-control"}))
    remarks = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={"placeholder":"Remarks", "class":"form-control"}), label="")

    class Meta:
        model = Customer
        exclude = ("user", "due_date")

    membership_days =  forms.IntegerField(required=True, initial=calendar.monthrange(timezone.now().year, timezone.now().month)[1], widget=forms.widgets.NumberInput(attrs={"placeholder":"Days paid for", "class":"form-control"}), label ="Days Paid")

    choices = [
        (1, "1 day"),
        (15, "15 days"),
        (calendar.monthrange(timezone.now().year, timezone.now().month)[1], "1 month")
    ]

    # membership =  forms.IntegerField(label="", widget=forms.Select(choices=choices, attrs={"class":"form-control"}))
    membership = forms.ChoiceField(label="", widget=forms.Select(
    attrs={'class': 'form-control'}),
    choices=choices)