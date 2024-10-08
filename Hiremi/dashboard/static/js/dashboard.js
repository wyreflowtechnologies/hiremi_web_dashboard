// for side nav bar
const doctToRight = document.querySelector("#dock-to-left")
const sideNav = document.querySelector(".side-navbar-container")
const sideNavOption = document.querySelectorAll(".side-navbar-container li a span")
const sideNavh1 = document.querySelectorAll(".side-navbar-container h1")
const sideNavIcon = document.querySelectorAll(".side-navbar-container li a i")

const dashboardBody = document.querySelector("#dash-board-body-wrap main")
console.log(dashboardBody);
// console.log(doctToRight);
// console.log(sideNav);
// console.log(sideNavOption);
// console.log(sideNavh1);
// console.log(sideNavIcon);


function liDisplayNone() {
    sideNavOption.forEach((span) => {
        span.style.display = "none"
    });
    sideNavh1.forEach((h1) => {
        h1.style.display = "none"
    })
}
function liDisplayBlock() {
    sideNavOption.forEach((span) => {
        span.style.display = "block"
    });

    sideNavh1.forEach((h1) => {
        h1.style.display = "block"
    })
}

doctToRight.addEventListener("click", () => {
    if (sideNav.style.width === "60px") {
        sideNav.style.width = "100%"
        dashboardBody.style.left = "20%"
        dashboardBody.style.width = "80%"
        liDisplayBlock()
        sideNavIcon.forEach((icon) => {
            icon.classList.remove("active")
        })
    }

    else {
        sideNav.style.width = "60px"
        dashboardBody.style.left = "61px"// 1px extra to show the navside border
        dashboardBody.style.width = "95%"
        liDisplayNone()
        sideNavIcon.forEach((icon) => {
            icon.classList.add("active")
            icon.style.marginLeft = "10px"
        })

    }
})


// to go-to top of the dashboard
function scrollTotop() {
    // console.log("clicked");
    document.querySelector(".dashboard-container").scrollTo({
        top: 0,
        behavior: "smooth"
    });
}



// to change the pages with navbar
const pages = document.querySelectorAll("[data-page]")
const navLink = document.querySelectorAll("[data-nav-link]")

function removeNavbarStyle() {
    navLink.forEach((li) => {
        li.style.color = "#575E6A"
        li.parentElement.style.backgroundColor = "#ffffff"
        li.parentElement.style.borderLeft = "none"
    })
}

navLink.forEach((link) => {
    // console.log(link.lastElementChild.innerHTML.toLowerCase());

    link.addEventListener("click", () => {

        removeNavbarStyle();
        link.style.color = "#C1272D"
        link.parentElement.style.backgroundColor = "#F4F6F9"
        link.parentElement.style.borderLeft = "4px solid #C1272D"


        pages.forEach((page) => {
            if (link.lastElementChild.innerHTML.toLowerCase() === page.dataset.page) {
                page.style.display = "block"
                scrollTotop()
            }

            else {
                page.style.display = "none"
            }
        })
    })
})






// to show the table

const boxLink = document.querySelectorAll("[box-link]")
const tableId = document.querySelectorAll("[table-id]")

boxLink.forEach((box) => {

    box.addEventListener("click", (evt) => {

        tableId.forEach((id) => {
            if (box.getAttribute("box-link").toLocaleLowerCase() === id.getAttribute("table-id").toLocaleLowerCase()) {

                id.style.display = "block"
            }
            else {
                id.style.display = "none"
            }
        })
    })
})






// query js

// for four query table 
let queryBtns = document.querySelectorAll("[query-btn]")
// console.log(queryBtns);
const queryHeading = document.querySelector(".query-list-heading h1")
// console.log(queryHeading);
let queryTables = document.querySelectorAll("[query-table]")
// console.log(queryTables);


queryBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        queryTables.forEach((table) => {
            if (btn.getAttribute("query-btn").toLocaleLowerCase() === table.getAttribute("query-table").toLocaleLowerCase()) {
                table.style.display = "block";
                queryHeading.innerHTML = btn.getAttribute("query-btn");
                // remove active from btn
                queryBtns.forEach((btn) => {
                    btn.classList.remove("active");
                })
                btn.classList.add("active")
            }
            else {
                table.style.display = "none"
            }

        })
    })
})



// to short the discrption in query table
const discrptions = document.querySelectorAll("#discript");
// console.log(discrptions);

function shortPara(para, numWords) {
    let paraGraph = para.split(" ");
    // console.log(paraGraph);
    if (paraGraph.length > numWords) {
        let shortPara = paraGraph.slice(0, numWords).join(" ") + "...";
        return shortPara;
    }
}

discrptions.forEach((discrpt) => {
    let para = discrpt.innerHTML;
    let result = shortPara(para, 3);
    // console.log(result);
    discrpt.innerHTML = result;
})


