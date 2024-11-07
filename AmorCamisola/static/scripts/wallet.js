document.addEventListener("DOMContentLoaded", function() {
    const showDepositBtn = document.getElementById("showDeposit");
    const showWithdrawalBtn = document.getElementById("showWithdrawal");
    const depositContainer = document.getElementById("depositContainer");
    const withdrawalContainer = document.getElementById("withdrawalContainer");

    // Show deposit form and hide withdrawal form
    showDepositBtn.addEventListener("click", function() {
        depositContainer.style.display = "block";
        withdrawalContainer.style.display = "none";
    });

    // Show withdrawal form and hide deposit form
    showWithdrawalBtn.addEventListener("click", function() {
        depositContainer.style.display = "none";
        withdrawalContainer.style.display = "block";
    });
});