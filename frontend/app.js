const reportsList = document.querySelector("#reports-list");
const reportsStatus = document.querySelector("#reports-status");
const savedReportsPanel = document.querySelector(
    "#saved-reports-panel",
);
const reportsBackdrop = document.querySelector("#reports-backdrop");
const openReportsButton = document.querySelector("#open-reports");
const closeReportsButton = document.querySelector("#close-reports");
const deleteAllReportsButton = document.querySelector(
    "#delete-all-reports",
);
const reportForm = document.querySelector("#report-form");
const formStatus = document.querySelector("#form-status");
const reportTitleInput = document.querySelector("#report-title");
const periodStartInput = document.querySelector("#period-start");
const periodEndInput = document.querySelector("#period-end");
const reportNotesInput = document.querySelector("#report-notes");
const reportDetails = document.querySelector("#report-details");
const detailsTitle = document.querySelector("#details-title");
const detailsPeriod = document.querySelector("#details-period");
const detailsIncome = document.querySelector("#details-income");
const detailsExpenses = document.querySelector("#details-expenses");
const incomeTotal = document.querySelector("#income-total");
const expenseTotal = document.querySelector("#expense-total");
const netBalance = document.querySelector("#net-balance");
const detailsNotes = document.querySelector("#details-notes");
const closeDetailsButton = document.querySelector("#close-details");
const incomeItems = document.querySelector("#income-items");
const expenseItems = document.querySelector("#expense-items");
const addIncomeButton = document.querySelector("#add-income");
const addExpenseButton = document.querySelector("#add-expense");
const lineItemTemplate = document.querySelector("#line-item-template");
const downloadPdfLink = document.querySelector("#download-pdf");

const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
});

let selectedReportId = null;
let reportCount = 0;

const formatMoney = (amount) => currencyFormatter.format(Number(amount));

const closeReportsPanel = () => {
    savedReportsPanel.classList.remove("is-open");
    savedReportsPanel.setAttribute("aria-hidden", "true");
    reportsBackdrop.hidden = true;
    openReportsButton.setAttribute("aria-expanded", "false");
    document.body.classList.remove("panel-open");
};

const openReportsPanel = () => {
    savedReportsPanel.classList.add("is-open");
    savedReportsPanel.setAttribute("aria-hidden", "false");
    reportsBackdrop.hidden = false;
    openReportsButton.setAttribute("aria-expanded", "true");
    document.body.classList.add("panel-open");
    closeReportsButton.focus();
};

const getResponseError = async (response, fallbackMessage) => {
    try {
        const body = await response.json();

        if (typeof body.detail === "string") {
            return body.detail;
        }

        if (Array.isArray(body.detail) && body.detail[0]?.msg) {
            return body.detail[0].msg;
        }
    } catch {
        // The response did not contain JSON.
    }

    return `${fallbackMessage} (${response.status})`;
};

const displayLineItems = (items, listElement, totalElement) => {
    listElement.replaceChildren();

    let total = 0;

    for (const item of items) {
        const listItem = document.createElement("li");
        const description = document.createElement("span");
        const amount = document.createElement("span");

        description.textContent = item.description;
        amount.textContent = formatMoney(item.amount);

        listItem.append(description, amount);
        listElement.append(listItem);
        total += Number(item.amount);
    }

    totalElement.textContent = `Total: ${formatMoney(total)}`;
    return total;
};

const showReport = async (reportId) => {
    reportsStatus.textContent = "Loading report details…";

    try {
        const response = await fetch(`/reports/${reportId}`);

        if (!response.ok) {
            const message = await getResponseError(
                response,
                "Unable to load report",
            );
            throw new Error(message);
        }

        const report = await response.json();
        selectedReportId = report.id;

        detailsTitle.textContent = report.title;
        detailsPeriod.textContent =
            `${report.reporting_period_start} to ` +
            `${report.reporting_period_end}`;

        const totalIncome = displayLineItems(
            report.income,
            detailsIncome,
            incomeTotal,
        );

        const totalExpenses = displayLineItems(
            report.expenses,
            detailsExpenses,
            expenseTotal,
        );

        netBalance.textContent =
            `Net balance: ${formatMoney(totalIncome - totalExpenses)}`;
        detailsNotes.textContent =
            report.notes || "No notes provided.";

        downloadPdfLink.href = `/reports/${report.id}/pdf`;
        downloadPdfLink.download = `report-${report.id}.pdf`;

        reportDetails.hidden = false;
        reportsStatus.textContent = "";
        closeReportsPanel();
        reportDetails.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    } catch (error) {
        console.error(error);
        reportsStatus.textContent =
            error instanceof Error
                ? error.message
                : "Unable to load report.";
    }
};

const addLineItem = (container) => {
    const templateCopy =
        lineItemTemplate.content.cloneNode(true);

    const lineItem =
        templateCopy.querySelector(".line-item");

    const removeButton =
        templateCopy.querySelector(".remove-line-item");

    removeButton.addEventListener("click", () => {
        lineItem.remove();
    });

    container.append(templateCopy);
};

const collectLineItems = (container) => {
    const rows = container.querySelectorAll(".line-item");

    return Array.from(rows).map((row) => {
        const description = row
            .querySelector(".line-item-description")
            .value
            .trim();

        const amount = row
            .querySelector(".line-item-amount")
            .value;

        return {
            description,
            amount,
        };
    });
};

async function loadReports() {
    try {
        const response = await fetch("/reports");

        if (!response.ok) {
            const message = await getResponseError(
                response,
                "Unable to load reports",
            );
            throw new Error(message);
        }

        const reports = await response.json();

        reportCount = reports.length;
        deleteAllReportsButton.disabled = reportCount === 0;
        reportsList.replaceChildren();
        openReportsButton.textContent =
            `Saved reports (${reports.length})`;

        if (reports.length === 0) {
            reportsStatus.textContent = "No reports saved yet.";
            reportDetails.hidden = true;
            selectedReportId = null;
            return;
        }

        reportsStatus.textContent = "";

        for (const report of reports) {
            const listItem = document.createElement("li");

            const viewButton = document.createElement("button");
            viewButton.type = "button";

            viewButton.textContent =
                `${report.title}: ` +
                `${report.reporting_period_start} to ` +
                `${report.reporting_period_end}`;

            viewButton.addEventListener("click", () => {
                void showReport(report.id);
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
                        const message = await getResponseError(
                            response,
                            "Unable to delete report",
                        );
                        throw new Error(message);
                    }

                    if (selectedReportId === report.id) {
                        reportDetails.hidden = true;
                        selectedReportId = null;
                    }

                    await loadReports();
                    reportsStatus.textContent =
                        `Deleted “${report.title}”.`;
                } catch (error) {
                    console.error(error);
                    reportsStatus.textContent =
                        error instanceof Error
                            ? error.message
                            : "Unable to delete report.";
                    deleteButton.disabled = false;
                }
            });

            listItem.append(viewButton, " ", deleteButton);
            reportsList.append(listItem);
        }
    } catch (error) {
        console.error(error);
        reportsStatus.textContent =
            error instanceof Error
                ? error.message
                : "Unable to load reports.";
    }
}

reportForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    formStatus.textContent = "Saving report…";

    try {
        const reportData = {
            title: reportTitleInput.value.trim(),
            reporting_period_start: periodStartInput.value,
            reporting_period_end: periodEndInput.value,
            income: collectLineItems(incomeItems),
            expenses: collectLineItems(expenseItems),
            notes: reportNotesInput.value.trim() || null,
        };

        const response = await fetch("/reports", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(reportData),
        });

        if (!response.ok) {
            const message = await getResponseError(
                response,
                "Unable to save report",
            );
            throw new Error(message);
        }

        const savedReport = await response.json();

        reportForm.reset();

        incomeItems.replaceChildren();
        expenseItems.replaceChildren();

        addLineItem(incomeItems);
        addLineItem(expenseItems);

        formStatus.textContent =
            `Saved “${savedReport.title}” successfully.`;

        await loadReports();
    } catch (error) {
        console.error(error);
        formStatus.textContent =
            error instanceof Error
                ? error.message
                : "Unable to save report.";
    }
});

addIncomeButton.addEventListener("click", () => {
    addLineItem(incomeItems);
});

addExpenseButton.addEventListener("click", () => {
    addLineItem(expenseItems);
});

addLineItem(incomeItems);
addLineItem(expenseItems);

openReportsButton.addEventListener("click", () => {
    openReportsPanel();
});

closeReportsButton.addEventListener("click", () => {
    closeReportsPanel();
});

reportsBackdrop.addEventListener("click", () => {
    closeReportsPanel();
});

deleteAllReportsButton.addEventListener(
    "click",
    async () => {
        const confirmation = window.prompt(
            (
                `This will permanently delete all ${reportCount} ` +
                `saved reports and their line items.\n\n` +
                `Downloaded PDF files will not be deleted.\n\n` +
                `Type DELETE ALL to continue.`
            ),
        );

        if (confirmation !== "DELETE ALL") {
            return;
        }

        deleteAllReportsButton.disabled = true;
        reportsStatus.textContent = "Deleting all reports…";

        try {
            const response = await fetch("/reports", {
                method: "DELETE",
            });

            if (!response.ok) {
                const message = await getResponseError(
                    response,
                    "Unable to delete all reports",
                );
                throw new Error(message);
            }

            const result = await response.json();

            reportDetails.hidden = true;
            selectedReportId = null;

            await loadReports();

            reportsStatus.textContent =
                `Deleted ${result.deleted_count} reports.`;
        } catch (error) {
            console.error(error);

            reportsStatus.textContent =
                error instanceof Error
                    ? error.message
                    : "Unable to delete all reports.";

            deleteAllReportsButton.disabled = reportCount === 0;
        }
    },
);

document.addEventListener("keydown", (event) => {
    if (
        event.key === "Escape" &&
        savedReportsPanel.classList.contains("is-open")
    ) {
        closeReportsPanel();
        openReportsButton.focus();
    }
});

closeDetailsButton.addEventListener("click", () => {
    reportDetails.hidden = true;
});

void loadReports();
