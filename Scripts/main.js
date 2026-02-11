window.onload = function() {
    const selectElement = document.getElementById("theme-select");

    if(selectElement){
        document.querySelector("body").className = selectElement.value;

        selectElement.addEventListener("change", (event) => {
            document.querySelector("body").className = event.target.value;
        });
    } else {
        console.log("Theme select not found!");
    }
}

