import capsolver

capsolver.api_key = "CAP-9AA533B78159C6463FCD7EF7324042D2"
solution = capsolver.solve({
    "type": "HCaptchaTask",
    "websiteURL": "stealthwriter.ai",
    "websiteKey": "5b13169c-1aa2-4267-8da1-0ebd54b6596a",
})
print(solution)