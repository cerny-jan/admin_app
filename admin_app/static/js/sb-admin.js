(function($) {
  "use strict"; // Start of use strict
  // Configure tooltips for collapsed side navigation
  $('.navbar-sidenav [data-toggle="tooltip"]').tooltip({
    template: '<div class="tooltip navbar-sidenav-tooltip" role="tooltip" style="pointer-events: none;"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
  })
  // Toggle the side navigation
  $("#sidenavToggler").click(function(e) {
    e.preventDefault();
    $("body").toggleClass("sidenav-toggled");
    $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
    $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
  });
  // Force the toggled class to be removed when a collapsible nav link is clicked
  $(".navbar-sidenav .nav-link-collapse").click(function(e) {
    e.preventDefault();
    $("body").removeClass("sidenav-toggled");
  });
  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .navbar-sidenav, body.fixed-nav .sidenav-toggler, body.fixed-nav .navbar-collapse').on('mousewheel DOMMouseScroll', function(e) {
    var e0 = e.originalEvent,
      delta = e0.wheelDelta || -e0.detail;
    this.scrollTop += (delta < 0 ? 1 : -1) * 30;
    e.preventDefault();
  });
  // Scroll to top button appear
  $(document).scroll(function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });
  // Configure tooltips globally
  $('[data-toggle="tooltip"]').tooltip()
  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function(event) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    event.preventDefault();
  });

  $('#editModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var username = button.data('username');
    var email = button.data('email');
    var userid = button.data('userid');
    var modal = $(this);
    modal.find('.modal-body input.username').val(username);
    modal.find('.modal-body input.email').val(email);
    $('#userid').val(userid);
  });

  $('#addProjectModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var google_email = button.data('google_email');
    var google_big_query_id = button.data('google_big_query_id');
    $('#google_email').val(google_email);
    $('#google_big_query_id').val(google_big_query_id);
  });

  $('#removeProjectModal').on('show.bs.modal', function(event) {
    var button = $(event.relatedTarget);
    var google_project_id = button.data('google_project_id');
    var modal = $(this);
    var href = modal.find('.modal-footer a').attr('href');
    href += google_project_id;
    modal.find('.modal-footer a').attr('href', href);
  });

  $("input[type=submit]").click(function() {
    $("input[type=submit]").removeAttr("clicked");
    $(this).attr("clicked", "true");
  });

  $('form').submit(function(e) {
    var currentForm = $(this);
    var submitButtonName = $("input[type=submit][clicked=true]").attr('name');
    var data = $(this).serializeArray(); // convert form to array
    data.push({name: "submitButtonName", value: submitButtonName});
      $.ajax({
          type: "POST",
          url: this.action,
          data:  $.param(data),
          success: function(data) {
            switch (data.status) {
              case 'formErrors':
                  currentForm.find('input').removeClass('is-invalid');
                  currentForm.find('.invalid-feedback').remove();
                  for (var field in data.formErrors) {
                      var errorField = currentForm.find('.' + field);
                      errorField.addClass('is-invalid');
                      errorField.after('<div class="invalid-feedback">' + data.formErrors[field] + '</div>');
                  }
                  break;
              case 'ok':
                localStorage.setItem('successMessage',data.message)
                location.reload();
                break;
              case 'error':
                $('.modal').modal('hide');
                $('.container-fluid').prepend('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Error: </strong>'+data.message+'<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
                break;
            }
              console.log(data)
          }
      });
      e.preventDefault();
  });


  // clear modal on close
  $('.modal').on('hidden.bs.modal', function(e) {
    $(this).find('form').removeClass('validated');
    $(this).find('input:text, input:password, input[name="email"]').val('').removeClass('is-invalid');
  });

  // onload messaging
  var successMessage = localStorage.getItem('successMessage');
  if (successMessage) {
    $('.container-fluid').prepend('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>Success: </strong>' + successMessage + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
    localStorage.removeItem('successMessage');
  }


})(jQuery); // End of use strict
