import { Application } from "stimulus"
import { definitionsFromContext } from "stimulus/webpack-helpers"

const application = Application.start();
const context = require.context("./public_controllers", true, /\.js$/);
application.load(definitionsFromContext(context));