
$(document).ready(function() {
    $('.js-example-basic-single').select2();
});

const button=document.querySelector('#search_button')
button.addEventListener('click',()=>{


const movie_id=$("#selections").val()

window.location.href=`/search/${movie_id}`
})