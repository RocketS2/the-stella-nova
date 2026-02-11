function changeTheme(theme) {
    localStorage.setItem("theme", theme);
    document.querySelector("body").dataset.theme = theme;
}

window.onload = function() {
    const selectElement = document.getElementById("theme-select");

    if(selectElement){
        let theme = localStorage.getItem("theme");
        if(theme){
            selectElement.value = theme;
        }
        theme = selectElement.value;
        changeTheme(theme);

        selectElement.addEventListener("change", (event) => {
            changeTheme(event.target.value);
        });
    } else {
        console.log("Theme select not found!");
    }
}

