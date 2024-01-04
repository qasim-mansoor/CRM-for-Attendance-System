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
            messages.success(request, "There was an error logging in. Please try again.")
            return redirect('home')
    else:
        return render(request, 'home.html', {'records':records})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
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
        messages.success(request, "You must be logged in to view this page.")
        return redirect('home')
    
def delete_record(request, pk):
    if request.user.is_authenticated:
        # delete_it = Customer.objects.get(id=pk)
        delete_it = get_object_or_404(Customer, id=pk)
        delete_it.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('home')
    else:
        messages.success(request, "You must be logged in to view this page.")
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
        messages.success(request, "You must be logged in to view this page.")
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
        messages.success(request, "You must be logged in to view this page.")
        return redirect('home')

def capture_image(request, file_path):
    # Initialize the camera
    # cap = cv2.VideoCapture("rtsp://admin:vaival123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1")
    cap = cv2.VideoCapture(0)
    # Check if the camera opened successfully
    if not cap.isOpened():
        messages.success(request, "Error: Could not open camera.")
        return

    # Capture a single frame
    ret, frame = cap.read()

    if not ret:
        messages.success(request, "Error: Could not capture frame.")
        cap.release()
        return

    # Save the captured frame as an image
    cv2.imwrite(file_path, frame)

    # Release the camera
    cap.release()

    messages.success(request, f"Image captured and saved as {file_path}")

def take_pictures(request, pk):
    if request.user.is_authenticated:
        # current_record = Customer.objects.get(id=pk)
        current_record = get_object_or_404(Customer, id=pk)
        template_name = './db2/' + str(pk) + ' ' + str(current_record.customer_name)
        # print(template_name)

        if not os.path.isdir(template_name):
            os.mkdir(template_name)

        # print(len(os.listdir(template_name)))

        
        capture_image(request, f'{template_name}/{current_record.customer_name}{len(os.listdir(template_name)) + 1}.jpg')

        return redirect("record", pk)
    

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


    
        
