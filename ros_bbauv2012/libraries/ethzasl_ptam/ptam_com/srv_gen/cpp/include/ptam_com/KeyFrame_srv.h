/* Auto-generated by genmsg_cpp for file /home/bbauvsbc1/bbauv_workspace/bbauv/ros_bbauv2012/libraries/ethzasl_ptam/ptam_com/srv/KeyFrame_srv.srv */
#ifndef PTAM_COM_SERVICE_KEYFRAME_SRV_H
#define PTAM_COM_SERVICE_KEYFRAME_SRV_H
#include <string>
#include <vector>
#include <map>
#include <ostream>
#include "ros/serialization.h"
#include "ros/builtin_message_traits.h"
#include "ros/message_operations.h"
#include "ros/time.h"

#include "ros/macros.h"

#include "ros/assert.h"

#include "ros/service_traits.h"



#include "geometry_msgs/PoseWithCovarianceStamped.h"

namespace ptam_com
{
template <class ContainerAllocator>
struct KeyFrame_srvRequest_ {
  typedef KeyFrame_srvRequest_<ContainerAllocator> Type;

  KeyFrame_srvRequest_()
  : flags(0)
  {
  }

  KeyFrame_srvRequest_(const ContainerAllocator& _alloc)
  : flags(0)
  {
  }

  typedef int32_t _flags_type;
  int32_t flags;


  typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator>  const> ConstPtr;
  boost::shared_ptr<std::map<std::string, std::string> > __connection_header;
}; // struct KeyFrame_srvRequest
typedef  ::ptam_com::KeyFrame_srvRequest_<std::allocator<void> > KeyFrame_srvRequest;

typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvRequest> KeyFrame_srvRequestPtr;
typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvRequest const> KeyFrame_srvRequestConstPtr;


template <class ContainerAllocator>
struct KeyFrame_srvResponse_ {
  typedef KeyFrame_srvResponse_<ContainerAllocator> Type;

  KeyFrame_srvResponse_()
  : KFids()
  , KFs()
  {
  }

  KeyFrame_srvResponse_(const ContainerAllocator& _alloc)
  : KFids(_alloc)
  , KFs(_alloc)
  {
  }

  typedef std::vector<uint32_t, typename ContainerAllocator::template rebind<uint32_t>::other >  _KFids_type;
  std::vector<uint32_t, typename ContainerAllocator::template rebind<uint32_t>::other >  KFids;

  typedef std::vector< ::geometry_msgs::PoseWithCovarianceStamped_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::geometry_msgs::PoseWithCovarianceStamped_<ContainerAllocator> >::other >  _KFs_type;
  std::vector< ::geometry_msgs::PoseWithCovarianceStamped_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::geometry_msgs::PoseWithCovarianceStamped_<ContainerAllocator> >::other >  KFs;


  typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator>  const> ConstPtr;
  boost::shared_ptr<std::map<std::string, std::string> > __connection_header;
}; // struct KeyFrame_srvResponse
typedef  ::ptam_com::KeyFrame_srvResponse_<std::allocator<void> > KeyFrame_srvResponse;

typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvResponse> KeyFrame_srvResponsePtr;
typedef boost::shared_ptr< ::ptam_com::KeyFrame_srvResponse const> KeyFrame_srvResponseConstPtr;

struct KeyFrame_srv
{

typedef KeyFrame_srvRequest Request;
typedef KeyFrame_srvResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;
}; // struct KeyFrame_srv
} // namespace ptam_com

namespace ros
{
namespace message_traits
{
template<class ContainerAllocator> struct IsMessage< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > : public TrueType {};
template<class ContainerAllocator> struct IsMessage< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator>  const> : public TrueType {};
template<class ContainerAllocator>
struct MD5Sum< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > {
  static const char* value() 
  {
    return "a30a7f59abf4e16357e66b71b9eaae25";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> &) { return value(); } 
  static const uint64_t static_value1 = 0xa30a7f59abf4e163ULL;
  static const uint64_t static_value2 = 0x57e66b71b9eaae25ULL;
};

template<class ContainerAllocator>
struct DataType< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > {
  static const char* value() 
  {
    return "ptam_com/KeyFrame_srvRequest";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator>
struct Definition< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > {
  static const char* value() 
  {
    return "int32 flags\n\
\n\
";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator> struct IsFixedSize< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > : public TrueType {};
} // namespace message_traits
} // namespace ros


namespace ros
{
namespace message_traits
{
template<class ContainerAllocator> struct IsMessage< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > : public TrueType {};
template<class ContainerAllocator> struct IsMessage< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator>  const> : public TrueType {};
template<class ContainerAllocator>
struct MD5Sum< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > {
  static const char* value() 
  {
    return "d865cbd185d5633ac1d50184eb2a3461";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> &) { return value(); } 
  static const uint64_t static_value1 = 0xd865cbd185d5633aULL;
  static const uint64_t static_value2 = 0xc1d50184eb2a3461ULL;
};

template<class ContainerAllocator>
struct DataType< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > {
  static const char* value() 
  {
    return "ptam_com/KeyFrame_srvResponse";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator>
struct Definition< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > {
  static const char* value() 
  {
    return "uint32[]   KFids\n\
geometry_msgs/PoseWithCovarianceStamped[]   KFs\n\
\n\
\n\
================================================================================\n\
MSG: geometry_msgs/PoseWithCovarianceStamped\n\
# This expresses an estimated pose with a reference coordinate frame and timestamp\n\
\n\
Header header\n\
PoseWithCovariance pose\n\
\n\
================================================================================\n\
MSG: std_msgs/Header\n\
# Standard metadata for higher-level stamped data types.\n\
# This is generally used to communicate timestamped data \n\
# in a particular coordinate frame.\n\
# \n\
# sequence ID: consecutively increasing ID \n\
uint32 seq\n\
#Two-integer timestamp that is expressed as:\n\
# * stamp.secs: seconds (stamp_secs) since epoch\n\
# * stamp.nsecs: nanoseconds since stamp_secs\n\
# time-handling sugar is provided by the client library\n\
time stamp\n\
#Frame this data is associated with\n\
# 0: no frame\n\
# 1: global frame\n\
string frame_id\n\
\n\
================================================================================\n\
MSG: geometry_msgs/PoseWithCovariance\n\
# This represents a pose in free space with uncertainty.\n\
\n\
Pose pose\n\
\n\
# Row-major representation of the 6x6 covariance matrix\n\
# The orientation parameters use a fixed-axis representation.\n\
# In order, the parameters are:\n\
# (x, y, z, rotation about X axis, rotation about Y axis, rotation about Z axis)\n\
float64[36] covariance\n\
\n\
================================================================================\n\
MSG: geometry_msgs/Pose\n\
# A representation of pose in free space, composed of postion and orientation. \n\
Point position\n\
Quaternion orientation\n\
\n\
================================================================================\n\
MSG: geometry_msgs/Point\n\
# This contains the position of a point in free space\n\
float64 x\n\
float64 y\n\
float64 z\n\
\n\
================================================================================\n\
MSG: geometry_msgs/Quaternion\n\
# This represents an orientation in free space in quaternion form.\n\
\n\
float64 x\n\
float64 y\n\
float64 z\n\
float64 w\n\
\n\
";
  }

  static const char* value(const  ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> &) { return value(); } 
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

template<class ContainerAllocator> struct Serializer< ::ptam_com::KeyFrame_srvRequest_<ContainerAllocator> >
{
  template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
  {
    stream.next(m.flags);
  }

  ROS_DECLARE_ALLINONE_SERIALIZER;
}; // struct KeyFrame_srvRequest_
} // namespace serialization
} // namespace ros


namespace ros
{
namespace serialization
{

template<class ContainerAllocator> struct Serializer< ::ptam_com::KeyFrame_srvResponse_<ContainerAllocator> >
{
  template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
  {
    stream.next(m.KFids);
    stream.next(m.KFs);
  }

  ROS_DECLARE_ALLINONE_SERIALIZER;
}; // struct KeyFrame_srvResponse_
} // namespace serialization
} // namespace ros

namespace ros
{
namespace service_traits
{
template<>
struct MD5Sum<ptam_com::KeyFrame_srv> {
  static const char* value() 
  {
    return "1950b962db053cd38d36594521dda474";
  }

  static const char* value(const ptam_com::KeyFrame_srv&) { return value(); } 
};

template<>
struct DataType<ptam_com::KeyFrame_srv> {
  static const char* value() 
  {
    return "ptam_com/KeyFrame_srv";
  }

  static const char* value(const ptam_com::KeyFrame_srv&) { return value(); } 
};

template<class ContainerAllocator>
struct MD5Sum<ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > {
  static const char* value() 
  {
    return "1950b962db053cd38d36594521dda474";
  }

  static const char* value(const ptam_com::KeyFrame_srvRequest_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator>
struct DataType<ptam_com::KeyFrame_srvRequest_<ContainerAllocator> > {
  static const char* value() 
  {
    return "ptam_com/KeyFrame_srv";
  }

  static const char* value(const ptam_com::KeyFrame_srvRequest_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator>
struct MD5Sum<ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > {
  static const char* value() 
  {
    return "1950b962db053cd38d36594521dda474";
  }

  static const char* value(const ptam_com::KeyFrame_srvResponse_<ContainerAllocator> &) { return value(); } 
};

template<class ContainerAllocator>
struct DataType<ptam_com::KeyFrame_srvResponse_<ContainerAllocator> > {
  static const char* value() 
  {
    return "ptam_com/KeyFrame_srv";
  }

  static const char* value(const ptam_com::KeyFrame_srvResponse_<ContainerAllocator> &) { return value(); } 
};

} // namespace service_traits
} // namespace ros

#endif // PTAM_COM_SERVICE_KEYFRAME_SRV_H
