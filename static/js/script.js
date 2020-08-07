$(document).ready(function(){

  $('input[name="phone"]').mask('+7(000)000-00-00');
  $('input[name="passport"]').mask('0000 000000');

  $('#getSms input[type="button"]').click(function(){
          $this = $(this).closest('#getSms');
          sms_type = $this.find('input[name="type"]').val();
          code = $this.find('input[name="code"]').val();
          action = $this.find('input[name="action"]').val();
                    $.ajax({
                        url: action,
                        dataType: 'json',
                        type: 'post',
                        data: 'phone='+$this.find('#phone').val()+'&type='+sms_type+'&code='+code,
                        beforeSend: function() {
                            $this.find('input[type="button"]').val('Ожидайте...');
                        },
                        success: function(json) {
                          console.log(json);
                          if(json['error'] == undefined){
                            $this.find('input[type="button"]').val('Далее');
                            if(action == '/sms'){
                              $this.find('.enter-phone').hide();
                              $this.find('input[name="action"]').val('/sms_check');
                              $this.find('.enter-code').show();
                              $('.w3-container').css('width', '50%').text('50%');
                            }if(action == '/sms_check'){
                              $('#getSms').hide();
                              if(sms_type == 'reg'){
                                $('.w3-container').css('width', '75%').text('75%');
                                $('#reg').show();
                                $('#reg input[name="phone"]').val($this.find('input[name="phone"]').val());
                              }
                            }if(json['success'] !== undefined){
                              $this.find('.form-success').show();
                              $this.find('.form-success').text(json['success']);
                            }
                          }else{
                            let form_error = $this.find('.error');
                            form_error.show().text(json['error']);
                            setTimeout(function(){$this.find('input[type="button"]').val('Далее');form_error.hide();}, 3000);
                          }
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            console.log(thrownError);
                            $this.val('Ошибка :(');
                            setTimeout(function(){$this.val('Далее');}, 3000);
                        }
                    });
  });

  $('.data-form').submit(function(){
    $this = $(this);
    action = $this.find('input[name="action"]').val();
    method = $this.find('input[name="method"]').val();
    btnval = $this.find('input[type="submit"]').val();
    formData = $this.serialize();
    ctype = 'application/x-www-form-urlencoded; charset=UTF-8';
    pdata = true;
    if(action == 'profile_picture'){
      formData = new FormData($('#'+action)[0]);
      ctype = false;
      pdata = false;
    }
                $.ajax({
                        url: method,
                        dataType: 'json',
                        type: 'post',
                        data: formData,
                        contentType: ctype,
                        processData: pdata,
                        beforeSend: function() {
                            $this.find('input[type="submit"]').val('Ожидайте...');
                        },
                        success: function(json) {
                          $this.find('input[type="button"]').val(btnval);
                          if(json['error'] == undefined){
                            if(action == 'reg'){
                              $this.hide();
                              $('.w3-container').css('width', '100%').text('100%');
                              $('#finish').show();
                            }if(action == 'log'){
                              location.href = '/wallet';
                            }if(action == 'profile'){
                              
                            }if(action == 'profile_picture'){
                              location.reload();
                            }if(json['success'] !== undefined){
                              $this.find('.success').show().text(json['success']);
                              setTimeout(function(){$this.find('.success').hide();}, 3000);
                              setTimeout(function(){$this.find('input[type="button"], input[type="submit"]').val(btnval);}, 3000);
                            }
                          }else{
                            $this.find('.error').show().text(json['error']);
                            setTimeout(function(){$this.find('input[type="button"], input[type="submit"]').val(btnval);$this.find('.error').hide();}, 3000);
                          }
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            console.log(thrownError);
                            $this.val('Ошибка :(');
                            setTimeout(function(){$this.val('Далее');}, 3000);
                        }
                    });
                return false;
  });

$(document).on('click', '.action-btn', function(){
    $this = $(this);
    action = $this.attr('data-action');
    method = $this.attr('data-method');
    btnval = $this.val();
    formData = '';

    if(action == 'csv')
      formData = $('.search-form').serialize();

                $.ajax({
                        url: method,
                        dataType: 'json',
                        type: 'post',
                        data: formData,
                        beforeSend: function() {

                        },
                        success: function(json) {
                          console.log(json);
                          if(json['error'] == undefined){
                            if(action == 'csv'){
                              location.href = json['link'];
                            }
                          }else{
                            $this.val('Ошибка');
                            setTimeout(function(){$this.val(btnval);}, 3000);
                          }
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            console.log(thrownError);
                            $this.val('Ошибка :(');
                            setTimeout(function(){$this.val(btnval);}, 3000);
                        }
                    });
                return false;
  });

  $('.page-link').click(function(){
    let search = '';

    let from = $('.search-form input[name="from"]').val();
    let to = $('.search-form input[name="to"]').val();
    search += '&from=' + from + '&to=' + to; 
    location.href = $(this).attr('href') + search;
    return false;
  });

  $('.trans-range').click(function(){

    let range = $(this).attr('data-range');
    let start, end;

    if(range == 'today'){
      start = new Date();
      end = new Date();
      end.setDate(end.getDate()+1);
    }else if(range == 'yesterday'){
      start = new Date();
      start.setDate(start.getDate()-1);
      end = new Date();
      end.setDate(end.getDate());
    }else{
      start = new Date();
      start.setDate(start.getDate()-7);
      end = new Date();
      end.setDate(end.getDate() + 1);
    }

    location.href = $(this).attr('href') + '?from=' + formatDate(start) + '&to=' + formatDate(end);
    return false;
  });

  $(document).on('click', '.btn-grey', function(){
    let btnblue = $(this).siblings('.btn-blue');
    btnblue.removeClass('btn-blue').addClass('btn-grey');
    $(this).removeClass('btn-grey').addClass('btn-blue');
  });
  $(document).on('click', '.btn-tog', function(){
    action = $(this).attr('data-action');
    $('.modal-block-form').hide();
    $('#'+action+'-tog').show();
    return false;
  });

  profilePicLoad();

  $("input[name='img']").change(function(){
    readURL(this);
  });

});

$('.copy-link').click(function(){
  copyToClipboard($('#payment-link').val());
  let $this = $(this);
  $this.val('Скопировано');
  $this.css('opacity', '.8');
  setTimeout(function(){$this.val('Скопировать');$this.css('opacity', '1');}, 2000);
});

function copyToClipboard(text) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val(text).select();
  document.execCommand("copy");
  $temp.remove();
}

function formatDate(day){

  let dd = day.getDate();
  let mm = day.getMonth() + 1;
  let yyyy = day.getFullYear();
  if (dd < 10) {
    dd = '0' + dd;
  } 
  if (mm < 10) {
    mm = '0' + mm;
  }
  day = yyyy + '-' + mm + '-' + dd;
  return day;
}

function profilePicLoad(){
  $('.profile_pic').each(function(){
    let $this = $(this);
    if(!$this.find('.profile-outer').length && !$this.find('i').length){
      let file = $this.attr('data-file');
      let img_url = '/static/upload/profile/'+file+'.png';
      $.get(img_url).done(function() {
        $this.append('<div class="profile-outer" style="background-image: url('+img_url+'?t='+Date.now()+');"></div>');
      }).fail(function() {
        $this.prepend('<i class="fa fa-user"></i>');
      });
    }
  });
}

function readURL(input) {
  if (input.files && input.files[0]) {
    let reader = new FileReader();

    reader.onload = function (e) {
      $('.data-form .profile_pic i, .data-form .profile_pic .profile-outer').remove();
      $('.data-form .profile_pic').append('<div class="profile-outer" style="background-image: url('+e.target.result+');"></div>');
    }

    reader.readAsDataURL(input.files[0]);
  }
}