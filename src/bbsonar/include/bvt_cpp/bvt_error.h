/*
    This file has been generated by bvtidl.pl. DO NOT MODIFY!
*/
#ifndef __CPP_BVTERROR_H__
#define __CPP_BVTERROR_H__

#include <string>
#include <bvt_cpp/bvt_retval.h>

namespace BVTSDK
{

/** The Error object provides access to the SDKs error reporting 
 * system.  This allows the user to map from an error number to 
 * a human readable description of the error.
 */
class Error
{
public:
	/** Return a description of the error
	 * \param code Error code 
	 */
	static std::string GetString(RetVal code)
	{
		return BVTError_GetString( code );
	}

	/** Return a string version of the name of the error constant.
	 * \param code Error code 
	 */
	static std::string GetName(RetVal code)
	{
		return BVTError_GetName( code );
	}


};
}

#endif
