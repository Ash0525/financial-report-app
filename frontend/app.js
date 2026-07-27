const reportsList = document.querySelector("#reports-list");
const reportsStatus = document.querySelector("#reports-status");
const reportForm = document.querySelector("#report-form");
const formStatus = document.querySelector("#form-status");

// Detail descriptions
const reportDetails = document.querySelector("#report-details");
const detailsTitle = document.querySelector("#details-title");
const detailsPeriod = document.querySelector("#details-period");
const detailsIncome = document.querySelector("#details-income");
const detailsExpenses = document.querySelector("#details-expenses");
const incomeTotal = document.querySelector("#income-total");
const expenseTotal = document.querySelector("#expense-total");
const detailsNotes = document.querySelector("#details-notes");
const closeDetailsButton = document.querySelector("#close-details");

// Formatting functions
const formatMoney = (amount) => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
    }).format(Number(amount));
};

const displayLineItems = (items, listElement, totalElement) => {
    listElement.replaceChildren();

    let total = 0;

    for (const item of items) {
        const listItem = document.createElement("li");

        listItem.textContent = `${item.description}: ${formatMoney(item.amount)}`;

        listElement.append(listItem);
        total += Number(item.amount);
    }

    totalElement.textContent = `Total: ${formatMoney(total)}`;
}

// Detail request async
const showReport = async (reportId) => {
    reportsStatus.textContent = "Loading report details...";

    try {
        const response = await fetch(`/reports/${reportId}`);

        if (!response.ok) {
            throw new Error(
                `Unable to load report: ${response.status}`
            );
        }

        const report = await response.json();

        detailsTitle.textContent = report.title;
        detailsPeriod.textContent =
            `${report.reporting_period_start} to ` +
            `${report.reporting_period_end}`;

        displayLineItems(
            report.income,
            detailsIncome,
            incomeTotal,
        );

        displayLineItems(
            report.expenses,
            detailsExpenses,
            expenseTotal,
        );

        detailsNotes.textContent = 
            report.notes || "No notes provided.";

        reportDetails.hidden = false;
        reportsStatus.textContent = "";

    } catch (error) {
        console.error(error);
        reportsStatus.textContent = error.message;
    }
};

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
        // Await reports
        const response = await fetch("/reports");

        // If the reponse is not ok
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

            // Make list variable
            const listItem = document.createElement("li");

            const viewButton = document.createElement("button");
            viewButton.type = "button";

            viewButton.textContent =
                `${report.title}: ` +
                `${report.reporting_period_start} to ` +
                `${report.reporting_period_end}`;

            // If view button clicked, show report id
            viewButton.addEventListener("click", () => {
                showReport(report.id);
            });

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

            listItem.append(viewButton, " ", deleteButton);
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

// Close detail
closeDetailsButton.addEventListener("click", () => {
    reportDetails.hidden = true;
});

// Call async function
loadReports();