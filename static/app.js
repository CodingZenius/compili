const source = document.getElementById("source");
const output = document.getElementById("output");

const compileButton = document.getElementById("compile");
const clearButton = document.getElementById("clear");


compileButton.addEventListener("click", async () => {

    output.textContent = "Compiling...";

    try {

        const response = await fetch("/compile", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                code: source.value

            })

        });

        const result = await response.json();

        if (result.success) {

            output.textContent = result.javascript;

        } else {

            output.textContent =
`Compiler Error

${result.error}`;

        }

    } catch (err) {

        output.textContent =
`Server Error

${err}`;

    }

});


clearButton.addEventListener("click", () => {

    source.value = "";

    output.textContent = "";

});


source.addEventListener("keydown", (event) => {

    if (event.ctrlKey && event.key === "Enter") {

        compileButton.click();

    }

});
