from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Customer
from .forms import AddRecordForm
import cv2
from .livefeed import VideoCamera
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import os
import face_recognition
import datetime
from django.utils import timezone
from django.db.models import Q
import pickle

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
                records = Customer.objects.filter(id=filter)
            else:
                records = Customer.objects.filter(Q(customer_name__icontains=filter))
            post = True
        else:
            records = Customer.objects.all()
            post = False

        active = [True if x.last_paid < timezone.now() - datetime.timedelta(days=31) else False for x in records]
        print(active)
        records_info = zip(records, active)
        return render(request, 'all_records.html', {'records':records, "active":active, 'records_info':records_info, 'post':post})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def active_records(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filter = request.POST.get("filter")
            if filter.isnumeric():
                records = Customer.objects.filter(id=filter)
            else:
                records = Customer.objects.filter(Q(customer_name__icontains=filter))
            post = True
        else:
            records = Customer.objects.all()
            post = False

        # records = Customer.objects.all()
        active = [True if x.last_paid < timezone.now() - datetime.timedelta(days=31) else False for x in records]
        print(active)
        records_info = zip(records, active)
        return render(request, 'active_records.html', {'records':records, "active":active, 'records_info':records_info, 'post':post})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def inactive_records(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filter = request.POST.get("filter")
            if filter.isnumeric():
                records = Customer.objects.filter(id=filter)
            else:
                records = Customer.objects.filter(Q(customer_name__icontains=filter))
            post = True
        else:
            records = Customer.objects.all()
            post = False

        # records = Customer.objects.all()
        active = [True if x.last_paid < timezone.now() - datetime.timedelta(days=31) else False for x in records]
        print(active)
        records_info = zip(records, active)
        return render(request, 'inactive_records.html', {'records':records, "active":active, 'records_info':records_info, 'post':post})
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def customer_record(request, pk):
    if request.user.is_authenticated:
        # customer_record = Customer.objects.get(id=pk)
        customer_record = get_object_or_404(Customer, id=pk)
        template_name = './db2/' + str(pk) + ' ' + str(customer_record.customer_name)
        if not os.path.isdir(template_name):
            os.mkdir(template_name)
        images = os.listdir(template_name)
        # print(images)
        images_with_path = list(map(lambda x: str(pk) + ' ' + str(customer_record.customer_name) + '/' + x, images))
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
                add_record = form.save()
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

def capture_image(request, file_path):
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
        template_name = './db2/' + str(pk) + ' ' + str(current_record.customer_name)
        temp_template = './temp'
        # print(template_name)

        if not os.path.isdir(template_name):
            os.mkdir(template_name)

        # print(len(os.listdir(template_name)))
            
        # cv2.imwrite(f'{template_name}/{current_record.customer_name}{len(os.listdir(template_name)) + 1}.jpg', frame)

        
        frame = capture_image(request, f'{template_name}/{current_record.customer_name}{len(os.listdir(template_name)) + 1}.jpg')
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
        template_name = './db2/' + str(pk) + ' ' + str(current_record.customer_name)
        temp_template = './temp'
        img = cv2.imread(f'{temp_template}/temp{len(os.listdir(temp_template))}.jpg')
        cv2.imwrite(f'{template_name}/{pk} {current_record.customer_name}{len(os.listdir(template_name)) + 1}.jpg', img)
        messages.success(request, f'Image saved on {template_name}/{pk} {current_record.customer_name}{len(os.listdir(template_name))}.jpg')
        update_encodings(f"{template_name}/{pk} {current_record.customer_name}{len(os.listdir(template_name))}.jpg")
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


    
        
