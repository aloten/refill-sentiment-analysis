const fs = require("fs");
const xpath = require("xpath");
const dom = require("xmldom").DOMParser;
const simpleParser = require("mailparser").simpleParser;

let prodAutomaticRefillCount = 0;

// extract customer reply text from S3 objects, and save to csv
const main = () => {
	const replyData = [];
	let files = fs.readdirSync("../resources/s3_objects/");
	files
		.forEach(async (filename) => {
			const reply = await getReplyTextFromEmail(filename);
			// const line = {
			//     reply,
			//     s3ObjectName: filename
			// }
			// replyData.push(line);
			// if (replyData.length === files.length) {
			//     writeRepliesToCsv(replyData);
			// }
		})
        setTimeout(() => {
            console.log(prodAutomaticRefillCount);
        }, 40000);
};

const writeRepliesToCsv = (replyData) => {
	const filepath = "../resources/repliesV2.csv";
	let fileString = "";
	replyData.forEach((line) => {
		fileString += line.reply + ";" + line.s3ObjectName + "\n";
	});
	fs.writeFileSync(filepath, fileString);
};

/**
 * Filters down the s3object to get the specific client text reply in the email response
 */
const getReplyTextFromEmail = async (emailFilename) => {
	const s3Object = fs.readFileSync(`../resources/s3_objects/${emailFilename}`, {
		encoding: "utf8",
		flag: "r",
	});
	const filteredEmail = filterOutEmarsysForwardingData(s3Object);
	const htmlDoc = await getHTMLFromS3Object(filteredEmail);
    // Save HTML of an s3 object
	// if (emailFilename == "f1ti912gv1g0oucpfqfnq61rg1gtqqke2sqqf681") {
	// 	fs.writeFileSync(
	// 		`../resources/testData/html/${emailFilename}.html`,
	// 		htmlDoc.toString()
	// 	);
	// }
	return getReplyText(htmlDoc);
};

/**
 *
 * @param htmlDoc: the email DOM
 * @return text of the reply, including whitespace if applicable
 */
const getReplyText = (htmlDoc) => {
	try {
		const dataContainer1 = xpath.select("//*[1]/text()", htmlDoc);
		if (dataContainer1.length > 0) {
			const emailText = dataContainer1[0].data;
			if (emailText.trim().toUpperCase() == "REFILL") {
                prodAutomaticRefillCount++;
				return emailText;
			}
		}
		const dataContainer2 = xpath.select("//*/text()", htmlDoc);
		if (dataContainer2.length > 0) {
			let replyText = "";
			dataContainer2.forEach((element) => {
				replyText += element.data + " ";
			});
			// Remove junk and email chain history
			// Remove after and incl date
			replyText = replyText.replace(/(>|<|\[|\||_{3,}).*/g, "");
			replyText = replyText.replace(/"/g, "");
			replyText = replyText.replace(
				/On (Mon|Tue|Wed|Thu|Fri|Sat|Sun|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*/gi,
				""
			);
			replyText = replyText.replace(/On \d{1,2}\/\d{1,2}\/\d{2,4}.*/g, "");
			replyText = replyText.replace(
				/Sent (on|by|with|from|via).*|From:.*|Original message.*|reply2refill@t.covetrus.com.*|-{3,}.*|Get Outlook for.*/g,
				""
			);
			return replyText.trim().trim('"');
		} else {
			return "no match with xpath selection";
		}
	} catch (error) {
		console.log(error);
		return "error getting reply text: " + error.message;
	}
};

/**
 *    Checks if the email contains "Refill"
 *
 *    @param htmlDoc: the email DOM
 *    @return true if the user's email is only "Refill" (case-insensitive and ignoring whitespace), else false
 */
const containsRefill = (htmlDoc) => {
	const dataContainer = xpath.select("//*[1]/text()", htmlDoc);
	if (dataContainer.length > 0) {
		console.log("containsRefill() -> checking value: " + dataContainer[0].data);
		const emailText = dataContainer[0].data;
		return emailText.trim().toUpperCase() == "REFILL";
	} else {
		return false;
	}
};

/**
 *    Gets the necessary data from the lambda event's email message
 *
 *    @param event: the lambda event
 *    @return HTML DOM representing the email content
 */
const getHTMLFromS3Object = async (filteredEmail) => {
	const parsedEmail = await simpleParser(filteredEmail);
	const emailContent = parsedEmail.textAsHtml;
	const emailSubject = parsedEmail.subject;
	const originalHeader = parsedEmail.headers;
	const originalEmail = filteredEmail;

	const htmlDoc = new dom().parseFromString(
		parsedEmail.textAsHtml,
		"text/html"
	);

	return htmlDoc;
};

/**
 * Removes Emarsys forwarding data from the top of the email body, if necessary.
 *
 * The customer's reply is sent to a @t.covetrus.com email address, which forwards the
 * email to a @r2r.covetrus.com email address. In doing so, Emarsys prepends the email
 * body with text like so:
 *
 *
 * reply mail received from: <email_address>
 * ---------------------------------------------------------------------------=
 * -----
 * Subject: 'RE: Just reply to refill Revolution=C2=AE Cat for Fluffy'
 * ---------------------------------------------------------------------------=
 * -----
 * campaign's receiver:=20
 * ---------------------------------------------------------------------------=
 * -----
 * received on:=20
 * ---------------------------------------------------------------------------=
 * -----
 *
 *
 *
 * message:
 * ---------------------------------------------------------------------------=
 * -----
 * ---------------------------------------------------------------------------=
 * -----
 * <original_email_body>
 *
 *
 * where <original_email_body> is what the customer actually sent in the reply.
 *
 * Keep in mind that the email content type is quoted-printable, hence the = signs.
 *
 * @param emailFile: the plain text email (equivalent to a .eml file)
 * @return email with the extra Emarsys data removed
 */
const filterOutEmarsysForwardingData = (emailFile) => {
	// The new line chars in this text can be \n or \r\n, depending on the environment.
	// Within the AWS lambda, it is \r\n
	const regex = /reply\smail\sreceived\sfrom:.*?\smessage:[\s-=]*$/ims;
	if (regex.test(emailFile)) {
		return emailFile.replace(regex, "");
	} else {
		return emailFile;
	}
};

main();
