document.addEventListener('DOMContentLoaded', function() {
  // Mobile Navigation Toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navbarList = document.querySelector('.navbar-list');
  
  navToggle.addEventListener('click', function() {
    this.classList.toggle('active');
    navbarList.classList.toggle('active');
  });
  
  // Close mobile menu when clicking on a link
  const navLinks = document.querySelectorAll('.navbar-list a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navToggle.classList.remove('active');
      navbarList.classList.remove('active');
    });
  });
  
  // Hero Slider
  const slides = document.querySelectorAll('.slide');
  const prevBtn = document.querySelector('.prev');
  const nextBtn = document.querySelector('.next');
  let currentSlide = 0;
  
  function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
    currentSlide = index;
  }
  
  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }
  
  function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
  }
  
  nextBtn.addEventListener('click', nextSlide);
  prevBtn.addEventListener('click', prevSlide);
  
  // Auto slide change
  let slideInterval = setInterval(nextSlide, 5000);
  
  // Pause slider on hover
  const heroSlider = document.querySelector('.hero-slider');
  heroSlider.addEventListener('mouseenter', () => clearInterval(slideInterval));
  heroSlider.addEventListener('mouseleave', () => {
    slideInterval = setInterval(nextSlide, 5000);
  });
  
  // Menu Category Tabs
  const menuCategories = document.querySelectorAll('.menu-category');
  const menuGrids = document.querySelectorAll('.menu-grid');
  
  menuCategories.forEach(category => {
    category.addEventListener('click', function() {
      // Remove active class from all categories
      menuCategories.forEach(cat => cat.classList.remove('active'));
      
      // Add active class to clicked category
      this.classList.add('active');
      
      // Hide all menu grids
      menuGrids.forEach(grid => grid.classList.remove('active'));
      
      // Show the corresponding menu grid
      const categoryName = this.getAttribute('data-category');
      document.getElementById(`${categoryName}-menu`).classList.add('active');
    });
  });
  
  // Reviews Slider
  const reviews = document.querySelectorAll('.review');
  const dots = document.querySelector('.slider-dots');
  let currentReview = 0;
  
  // Create dots
  reviews.forEach((review, index) => {
    const dot = document.createElement('div');
    dot.classList.add('dot');
    if (index === 0) dot.classList.add('active');
    dot.addEventListener('click', () => showReview(index));
    dots.appendChild(dot);
  });
  
  function showReview(index) {
    reviews.forEach(review => review.classList.remove('active'));
    reviews[index].classList.add('active');
    
    const allDots = document.querySelectorAll('.dot');
    allDots.forEach(dot => dot.classList.remove('active'));
    allDots[index].classList.add('active');
    
    currentReview = index;
  }
  
  // Auto change reviews
  setInterval(() => {
    currentReview = (currentReview + 1) % reviews.length;
    showReview(currentReview);
  }, 6000);
  
  // Sticky Header
  const header = document.querySelector('.header');
  const topbarHeight = document.querySelector('.topbar').offsetHeight;
  
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > topbarHeight) {
      header.classList.add('sticky');
    } else {
      header.classList.remove('sticky');
    }
  });
  
  // Back to Top Button
  const backToTopBtn = document.querySelector('.back-to-top');
  
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopBtn.classList.add('active');
    } else {
      backToTopBtn.classList.remove('active');
    }
  });
  
  backToTopBtn.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
  
  // Smooth Scrolling for Anchor Links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = targetElement.offsetTop - headerHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Form Validation
  const contactForm = document.querySelector('.contact-form form');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get form values
      const name = this.querySelector('input[type="text"]').value.trim();
      const email = this.querySelector('input[type="email"]').value.trim();
      const phone = this.querySelector('input[type="tel"]').value.trim();
      const date = this.querySelector('input[type="date"]').value;
      
      // Simple validation
      if (!name) {
        alert('Please enter your name');
        return false;
      }
      
      if (!email || !email.includes('@')) {
        alert('Please enter a valid email address');
        return false;
      }
      
      if (!phone) {
        alert('Please enter your phone number');
        return false;
      }
      
      if (!date) {
        alert('Please select an event date');
        return false;
      }
      
      // If validation passes
      alert('Thank you for your booking request! We will contact you shortly.');
      this.reset();
      return true;
    });
  }
  
  // Initialize first slide and review as active
  showSlide(0);
  showReview(0);
});
