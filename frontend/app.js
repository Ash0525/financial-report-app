const reportsList = document.querySelector("#reports-list");
const reportsStatus = document.querySelector("#reports-status");
const reportForm = document.querySelector("#report-form");
const formStatus = document.querySelector("#form-status");

function createLineItems(descriptionId, amountId) {
    const description = document.querySelector(descriptionId).value.trim();
    const amount = document.querySelector(amountId).value;

    // Safety if
    if (!description && !amount) {
        return [];
    }

    if (!description || !amount) {
        throw new Error (
            "Each financial item needs a description and amount."
        );
    }

    return [
        {
            description,
            amount,
        },
    ];
}

async function loadReports() {
    try {
        const response = await fetch("/reports");

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        const reports = await response.json();

        reportsList.replaceChildren();

        if (reports.length === 0) {
            reportsStatus.textContent = "No reports saved yet.";
            return;
        }

        reportsStatus.textContent = "";

        // For every report in the list of report
        for (const report of reports) {
            const listItem = document.createElement("li");

            const reportText = document.createElement("span");
            reportText.textContent =
                `${report.title}: ` +
                `${report.reporting_period_start} to ` +
                `${report.reporting_period_end}`;

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", async () => {
                const shouldDelete = window.confirm(
                    `Delete “${report.title}”?`
                );

                if (!shouldDelete) {
                    return;
                }

                deleteButton.disabled = true;

                try {
                    const response = await fetch(
                        `/reports/${report.id}`,
                        {
                            method: "DELETE",
                        },
                    );

                    if (!response.ok) {
                        throw new Error(
                            `Unable to delete report: ${response.status}`
                        );
                    }

                    await loadReports();
                    reportsStatus.textContent =
                        `Deleted “${report.title}”.`;
                } catch (error) {
                    console.error(error);
                    reportsStatus.textContent = error.message;
                    deleteButton.disabled = false;
                }
            });

            listItem.append(reportText, " ", deleteButton);
            reportsList.append(listItem);
        }
    } catch (error) {
        console.error(error);
        reportsStatus.textContent = "Unable to load reports.";
    }
}

// Add event listeners
reportForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    formStatus.textContent = "Saving report...";

    try {
        const reportData = {
            title: document
                .querySelector("#report-title")
                .value
                .trim(),
            
            reporting_period_start: document
                .querySelector("#period-start")
                .value,

            reporting_period_end: document
                .querySelector("#period-end")
                .value,
            
            income: createLineItems(
                "#income-description",
                "#income-amount",
            ),

            expenses: createLineItems(
                "#expense-description",
                "#expense-amount",
            ),

            notes:
                document
                    .querySelector("#report-notes")
                    .value
                    .trim() || null,
        };

        const response = await fetch("/reports", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(reportData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error(errorData);

            throw new Error(
                `Unable to save report: ${response.status}`
            );
        }

        const savedReport = await response.json();

        reportForm.reset();
        formStatus.textContent = 
            `Saved "${savedReport.title}" successfully.`;

        await loadReports();
    } catch (error) {
        console.error(error);
        formStatus.textContent = error.message;
    }
});

// Call async function
loadReports();