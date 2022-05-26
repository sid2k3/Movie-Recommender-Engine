
$(document).ready(function() {
    $('.js-example-basic-single').select2({width:'50vw'});

});

const button=document.querySelector('#search_button')
button.addEventListener('click',()=>{

const selectedRadio=document.querySelector('input[name="radio"]:checked').id

let url
if (selectedRadio==='movie-radio')
{
const movie_id=document.querySelector('#selections').value
url=`/search/${movie_id}`

}
else
{
const genre=document.querySelector('#genre-selections').value
url=`/genre/${genre}`

}


window.location.href=url
})
const movieRadio=document.querySelector("#movie-radio")
const genreRadio=document.querySelector("#genre-radio")

movieRadio.addEventListener('click',()=>{
document.querySelector("#movie-div").classList.remove('hidden')

document.querySelector("#genre-div").classList.add('hidden')
})

genreRadio.addEventListener('click',()=>{
document.querySelector("#genre-div").classList.remove('hidden')

document.querySelector("#movie-div").classList.add('hidden')
})


