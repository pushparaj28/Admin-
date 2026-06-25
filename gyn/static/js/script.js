

document.addEventListener('DOMContentLoaded', function() {
    
    // Purana delete wala code yahan upar rahega...
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    // Har button par click event laga rahe hain
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Confirmation popup show karo
            const userConfirmed = confirm('Kya aap sach me is appointment ko delete karna chahte hain?');
            
            // Agar user ne 'Cancel' dabaya, to link open hone se rok do
            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });




    // --- TOAST AUTO-HIDE LOGIC ---
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(toast => {
        // 3.5 seconds ke baad 'hide' class add kardo
        setTimeout(() => {
            toast.classList.add('hide');
        
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 3500); 
    });
});